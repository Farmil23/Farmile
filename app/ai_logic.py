import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from flask import current_app

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from byteplussdkarkruntime import Ark

# --- 1. ARK WRAPPER FOR LANGCHAIN ---
class ArkChatModel(BaseChatModel):
    client: Any = None
    model_endpoint: str = ""

    def __init__(self, api_key: str, model_endpoint: str):
        super().__init__()
        self.client = Ark(
            api_key=api_key,
            base_url="https://ark.ap-southeast.bytepluses.com/api/v3"
        )
        self.model_endpoint = model_endpoint

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        ark_messages = []
        for msg in messages:
            role = "user"
            if isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            ark_messages.append({"role": role, "content": msg.content})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_endpoint,
                messages=ark_messages,
                **kwargs
            )
            content = completion.choices[0].message.content
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
        except Exception as e:
            # Fallback or error handling
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=f"Error: {str(e)}"))])

    @property
    def _llm_type(self) -> str:
        return "byteplus-ark"

def get_llm():
    return ArkChatModel(
        api_key=current_app.config.get('ARK_API_KEY'),
        model_endpoint=current_app.config.get('MODEL_ENDPOINT_ID')
    )

# --- 2. LIQUID SCHEDULER (LANGGRAPH AGENT) ---
# Note: Since I cannot install langgraph yet, I will simulate the logic with a simpler Agent-like structure
# or a strict Prompt Engineering approach that mimics the agent's decision making.
# Valid LangGraph implementation requires the library. I will write a mock-compatible structure.

def run_liquid_scheduler(user_query: str, user_schedule: str) -> Dict[str, Any]:
    """
    Simulates the Liquid Scheduler Agent.
    Input: "Bro, gue capek banget abis voli..."
    Output: JSON with action (reschedule) and response text.
    """
    llm = get_llm()
    
    system_prompt = f"""
    You are a 'Liquid Scheduler' Agent for a student. behavior: Dynamic, empathetic, flexible.
    
    GOAL: Adjust the schedule based on user's condition.
    
    CURRENT SCHEDULE CONTEXT:
    {user_schedule}
    
    LOGIC:
    1. Identify user's intent & condition (e.g., tired -> needs rest).
    2. Check schedule conflicts.
    3. Propose a MOVE for tasks to a better slot (e.g., tomorrow morning, saturday).
    4. Output accurate JSON ONLY designated by [JSON_START] and [JSON_END].
    
    JSON FORMAT:
    {{
        "action": "reschedule" | "none",
        "rationale": "start with empathy",
        "proposed_changes": [
            {{ "task_title": "Deep Learning", "new_slot": "Saturday, 09:00 AM" }}
        ],
        "reply_text": "Oke, istirahatlah. Sesi Deep Learning gue geser ke Sabtu jam 09.00 ya. Aman, masih keburu sebelum kuis."
    }}
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    
    response = llm.invoke(messages)
    content = response.content
    
    # Simple parsing (robust parsing would use regex)
    try:
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return data
    except:
        pass
        
    return {"action": "none", "reply_text": content}

# --- 3. SKS ESTIMATOR ---
def estimate_task_duration(task_title: str, page_count: int, is_coding: bool) -> int:
    llm = get_llm()
    
    prompt = f"""
    Estimate the duration (in minutes) for a student task.
    Task: {task_title}
    Pages: {page_count}
    Coding Involved: {is_coding}
    
    Logic: 
    - Reading: ~3-5 mins per page.
    - Coding: Adds significant time (1-3 hours usually depending on complexity implied by title).
    - Writing: ~30 mins per page.
    
    Return ONLY a single integer (minutes).
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        minutes = int(''.join(filter(str.isdigit, response.content)))
        return minutes
    except:
        return 60 # Default fallback

# --- 4. FEYNMAN INTERROGATOR ---
def feynman_test(topic: str, user_explanation: str = None, chat_history: List[Dict] = []) -> str:
    llm = get_llm()
    
    if not user_explanation:
        # Step 1: User just inputted the topic
        prompt = f"User wants to learn '{topic}' using Feynman Technique. Ask them to explain it simply."
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    # Step 2: Evaluate explanation
    history_messages = []
    for msg in chat_history:
        if msg['role'] == 'user': history_messages.append(HumanMessage(content=msg['content']))
        else: history_messages.append(AIMessage(content=msg['content']))
        
    system = "You are a Feynman Technique Tutor. Evaluate the user's explanation. Identify gaps. If good, ask deeper questions. If bad, correct gently."
    messages = [SystemMessage(content=system)] + history_messages + [HumanMessage(content=user_explanation)]
    
    response = llm.invoke(messages)
    return response.content

# --- 5. OVT PANIC BUTTON ---
def stoic_mentor(user_stats: Dict) -> Dict[str, Any]:
    llm = get_llm()
    
    stats_str = f"""
    GPA: {user_stats.get('gpa', 'N/A')}
    Completed Tasks this week: {user_stats.get('completed_tasks', 0)}
    Level: {user_stats.get('level', 1)}
    """
    
    prompt = f"""
    Act as a Stoic Mentor. The user is panicking/overthinking.
    Refute their anxiety using DATA.
    
    User Stats:
    {stats_str}
    
    Output JSON:
    {{
        "stoic_quote": "...",
        "data_analysis": "Data shows you have completed X tasks...",
        "reassurance": "You are doing fine."
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except:
        pass
        
    return {"reassurance": response.content}
