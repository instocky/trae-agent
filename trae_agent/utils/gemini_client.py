# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Google Gemini API client wrapper with tool integration."""

import os
import json
from typing import override

from google import genai
from google.genai import types

from ..tools.base import Tool, ToolCall, ToolResult
from ..utils.config import ModelParameters
from .base_client import BaseLLMClient
from .llm_basics import LLMMessage, LLMResponse, LLMUsage


class GeminiClient(BaseLLMClient):
    """Google Gemini client wrapper with tool schema generation."""

    def __init__(self, model_parameters: ModelParameters):
        super().__init__(model_parameters)

        # Get API key from environment if not provided or is placeholder
        if self.api_key == "" or self.api_key == "your_google_api_key":
            self.api_key: str = os.getenv("GOOGLE_API_KEY", "")

        if self.api_key == "" or self.api_key == "your_google_api_key":
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY in environment variables or config file.")

        # Initialize Gemini client
        self.client: genai.Client = genai.Client(api_key=self.api_key)
        self.message_history: list[types.Content] = []

    @override
    def set_chat_history(self, messages: list[LLMMessage]) -> None:
        """Set the chat history."""
        self.message_history = self.parse_messages_to_history(messages)

    @override
    def chat(self, messages: list[LLMMessage], model_parameters: ModelParameters, tools: list[Tool] | None = None, reuse_history: bool = True) -> LLMResponse:
        """Send chat messages to Gemini with optional tool support."""
        
        # Parse messages to Gemini format
        system_instruction = None
        contents = []
        
        for message in messages:
            if message.role == "system":
                # Gemini uses separate system_instruction parameter
                system_instruction = message.content
            elif message.role in ["user", "assistant"]:
                # Convert to Gemini Content format
                if message.role == "user":
                    gemini_role = "user"
                else:  # assistant
                    gemini_role = "model"
                
                if message.tool_call:
                    # Handle function calls - these come from assistant/model
                    function_call = types.FunctionCall(
                        name=message.tool_call.name,
                        args=message.tool_call.arguments
                    )
                    contents.append(types.Content(
                        role="model",  # Function calls always from model
                        parts=[types.Part(function_call=function_call)]
                    ))
                elif message.tool_result:
                    # Handle function responses - these always come from user
                    function_response = types.FunctionResponse(
                        name=message.tool_result.call_id.replace("call_", "") if message.tool_result.call_id else "unknown",
                        response={"result": message.tool_result.result or message.tool_result.error}
                    )
                    contents.append(types.Content(
                        role="user",  # Function responses always from user
                        parts=[types.Part(function_response=function_response)]
                    ))
                else:
                    # Regular text message
                    if message.content:
                        contents.append(types.Content(
                            role=gemini_role,
                            parts=[types.Part.from_text(text=message.content)]
                        ))

        # Prepare tool schemas if tools are provided
        tool_declarations = None
        if tools and self.supports_tool_calling(model_parameters):
            tool_declarations = []
            for tool in tools:
                # Convert tool to Gemini function declaration
                function_declaration = types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=self._convert_tool_schema(tool.get_input_schema())
                )
                tool_declarations.append(function_declaration)

        # Build generation config
        config = types.GenerateContentConfig(
            temperature=model_parameters.temperature,
            max_output_tokens=model_parameters.max_tokens,
            top_p=model_parameters.top_p,
            top_k=model_parameters.top_k,
        )
        
        # Add system instruction if present
        if system_instruction:
            config.system_instruction = system_instruction
            
        # Add tools if present
        if tool_declarations:
            config.tools = [types.Tool(function_declarations=tool_declarations)]

        try:
            # Make API call to Gemini
            response = self.client.models.generate_content(
                model=model_parameters.model,
                contents=contents,
                config=config
            )

            # Parse response to LLMResponse format
            llm_response = self._parse_response(response, model_parameters.model)

            # Record trajectory if recorder is available
            if self.trajectory_recorder:
                self.trajectory_recorder.record_llm_interaction(
                    messages=messages,
                    response=llm_response,
                    provider="gemini",
                    model=model_parameters.model,
                    tools=tools
                )

            return llm_response

        except Exception as e:
            raise

    @override
    def supports_tool_calling(self, model_parameters: ModelParameters) -> bool:
        """Check if the current Gemini model supports tool calling."""
        # Most Gemini models support function calling
        tool_capable_models = [
            "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", 
            "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"
        ]
        return any(model in model_parameters.model for model in tool_capable_models)

    def parse_messages_to_history(self, messages: list[LLMMessage]) -> list[types.Content]:
        """Parse messages to Gemini history format."""
        history = []
        for message in messages:
            if message.role in ["user", "assistant"]:
                gemini_role = "user" if message.role == "user" else "model"
                if message.content:
                    history.append(types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=message.content)]
                    ))
        return history

    def _parse_response(self, response: types.GenerateContentResponse, model: str) -> LLMResponse:
        """Convert Gemini response to LLMResponse format."""
        
        # Extract main text content
        content = response.text if response.text else ""
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage_meta = response.usage_metadata
            usage = LLMUsage(
                input_tokens=getattr(usage_meta, 'prompt_token_count', 0),
                output_tokens=getattr(usage_meta, 'candidates_token_count', 0),
                reasoning_tokens=getattr(usage_meta, 'thoughts_token_count', 0) or 0,
                cache_creation_input_tokens=getattr(usage_meta, 'cache_tokens_details', {}).get('cache_creation_input_tokens', 0) if getattr(usage_meta, 'cache_tokens_details', None) else 0,
                cache_read_input_tokens=getattr(usage_meta, 'cache_tokens_details', {}).get('cache_read_input_tokens', 0) if getattr(usage_meta, 'cache_tokens_details', None) else 0
            )

        # Extract finish reason
        finish_reason = None
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = str(candidate.finish_reason).replace('FinishReason.', '')

        # Extract tool calls if present
        tool_calls = []
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        func_call = part.function_call
                        tool_calls.append(ToolCall(
                            call_id=f"call_{hash(func_call.name)}",  # Generate ID
                            name=func_call.name,
                            arguments=dict(func_call.args) if func_call.args else {}
                        ))

        return LLMResponse(
            content=content,
            usage=usage,
            model=model,
            finish_reason=finish_reason,
            tool_calls=tool_calls if tool_calls else None
        )

    def _convert_tool_schema(self, schema: dict) -> types.Schema:
        """Convert tool schema to Gemini Schema format."""
        
        def convert_property(prop_schema: dict) -> types.Schema:
            """Convert a property schema recursively."""
            prop_type = prop_schema.get('type', 'STRING').upper()
            
            # Map JSON Schema types to Gemini types
            type_mapping = {
                'STRING': 'STRING',
                'INTEGER': 'INTEGER', 
                'NUMBER': 'NUMBER',
                'BOOLEAN': 'BOOLEAN',
                'ARRAY': 'ARRAY',
                'OBJECT': 'OBJECT'
            }
            
            gemini_type = type_mapping.get(prop_type, 'STRING')
            
            schema_args = {
                'type': gemini_type,
                'description': prop_schema.get('description', '')
            }
            
            # Handle array items
            if gemini_type == 'ARRAY' and 'items' in prop_schema:
                schema_args['items'] = convert_property(prop_schema['items'])
            
            # Handle object properties  
            if gemini_type == 'OBJECT' and 'properties' in prop_schema:
                properties = {}
                for name, prop in prop_schema['properties'].items():
                    properties[name] = convert_property(prop)
                schema_args['properties'] = properties
                
                if 'required' in prop_schema:
                    schema_args['required'] = prop_schema['required']
            
            return types.Schema(**schema_args)

        # Convert main schema
        properties = {}
        if 'properties' in schema:
            for name, prop in schema['properties'].items():
                properties[name] = convert_property(prop)

        return types.Schema(
            type='OBJECT',
            properties=properties,
            required=schema.get('required', [])
        )
