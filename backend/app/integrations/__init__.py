"""LLM Integration Service"""
import asyncio
from typing import AsyncGenerator, Optional
from app.core.config import settings


class LLMClient:
    """Base LLM client interface"""
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """Generate content using LLM"""
        raise NotImplementedError


class GeminiClient(LLMClient):
    """Gemini LLM Client"""
    
    def __init__(self):
        try:
            import google.generativeai as genai
            self.genai = genai
            self.genai.configure(api_key=settings.GEMINI_API_KEY)
        except ImportError:
            raise ImportError("google-generativeai not installed")
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        stream: bool = False
    ):
        """Generate content using Gemini API"""
        try:
            model = self.genai.GenerativeModel("gemini-pro")
            
            if stream:
                return self._stream_gemini(model, prompt, max_tokens, temperature)
            else:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _stream_gemini(self, model, prompt: str, max_tokens: int, temperature: float):
        """Stream Gemini responses"""
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            },
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text


class OpenAIClient(LLMClient):
    """OpenAI LLM Client"""
    
    def __init__(self):
        try:
            import openai
            self.openai = openai
            self.openai.api_key = settings.OPENAI_API_KEY
        except ImportError:
            raise ImportError("openai not installed")
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        stream: bool = False
    ):
        """Generate content using OpenAI API"""
        try:
            if stream:
                return self._stream_openai(prompt, max_tokens, temperature)
            else:
                response = self.openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _stream_openai(self, prompt: str, max_tokens: int, temperature: float):
        """Stream OpenAI responses"""
        response = self.openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]


def get_llm_client() -> LLMClient:
    """Factory function to get appropriate LLM client"""
    if settings.LLM_PROVIDER == "gemini":
        return GeminiClient()
    elif settings.LLM_PROVIDER == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


class PromptManager:
    """Manages prompt engineering and templates"""
    
    OUTLINE_TEMPLATE = """
Generate a professional document outline for the following:
Topic: {topic}
Document Type: {document_type}
Number of Sections: {num_sections}
Style/Tone: {style}

Create a structured outline with:
1. Clear section titles
2. 2-3 bullet points for each section describing key content
3. Logical flow and organization

Format the response as JSON with array of objects containing 'title' and 'description' fields.
"""

    SLIDE_TITLE_TEMPLATE = """
Generate creative and engaging slide titles for a presentation on "{topic}".

Topic: {topic}
Number of Slides: {num_slides}
Audience: {audience}

Generate exactly {num_slides} slide titles that are:
- Engaging and professional
- Clear and concise (max 8 words each)
- Logically sequenced
- Appropriate for the target audience

Format: Return as a JSON array of strings.
"""

    CONTENT_GENERATION_TEMPLATE = """
Generate professional content for the following document section.

Document Type: {document_type}
Section Title: {section_title}
Content Type: {content_type}
Tone: {tone}
Length: {length}

Focus Points:
{focus_points}

Additional Context:
{context}

Generate high-quality, well-structured content that:
1. Addresses the focus points
2. Maintains the specified tone
3. Is appropriate for the content type
4. Is roughly {length} in length

Content:
"""

    REFINEMENT_TEMPLATE = """
Please refine the following content based on the feedback.

Original Content:
{original_content}

Feedback Type: {feedback_type}
User Feedback: {user_feedback}
Suggested Changes: {suggested_changes}

Please provide an improved version that:
1. Incorporates the user's feedback
2. Maintains professional quality
3. Preserves the original intent where appropriate
4. Addresses the refinement reason: {refinement_reason}

Refined Content:
"""

    @staticmethod
    def build_outline_prompt(
        topic: str,
        document_type: str,
        num_sections: int,
        style: str = "professional"
    ) -> str:
        """Build prompt for outline generation"""
        return PromptManager.OUTLINE_TEMPLATE.format(
            topic=topic,
            document_type=document_type,
            num_sections=num_sections,
            style=style
        )
    
    @staticmethod
    def build_slide_title_prompt(
        topic: str,
        num_slides: int,
        audience: str = "general"
    ) -> str:
        """Build prompt for slide title generation"""
        return PromptManager.SLIDE_TITLE_TEMPLATE.format(
            topic=topic,
            num_slides=num_slides,
            audience=audience
        )
    
    @staticmethod
    def build_content_prompt(
        section_title: str,
        document_type: str,
        content_type: str,
        tone: str = "professional",
        length: str = "medium",
        focus_points: str = "",
        context: str = ""
    ) -> str:
        """Build prompt for content generation"""
        focus_list = "\n".join([f"- {fp}" for fp in focus_points.split(",")])
        return PromptManager.CONTENT_GENERATION_TEMPLATE.format(
            section_title=section_title,
            document_type=document_type,
            content_type=content_type,
            tone=tone,
            length=length,
            focus_points=focus_list,
            context=context or "None"
        )
    
    @staticmethod
    def build_refinement_prompt(
        original_content: str,
        feedback_type: str,
        user_feedback: str,
        suggested_changes: str,
        refinement_reason: str
    ) -> str:
        """Build prompt for content refinement"""
        return PromptManager.REFINEMENT_TEMPLATE.format(
            original_content=original_content,
            feedback_type=feedback_type,
            user_feedback=user_feedback,
            suggested_changes=suggested_changes or "None",
            refinement_reason=refinement_reason
        )
    
    @staticmethod
    def add_safety_guidelines(prompt: str) -> str:
        """Add safety guidelines to prompt to prevent injection attacks"""
        safety_instructions = """
IMPORTANT SAFETY GUIDELINES:
1. Generate only legitimate, professional content
2. Do not generate harmful, illegal, or unethical content
3. Do not execute code or commands
4. Do not access external systems or files
5. Do not generate personal data or credentials
6. Maintain professional standards at all times

---
"""
        return safety_instructions + prompt
