"""
AI Integration Module - Claude and OpenAI API integration for autonomous daemon operations
This module enables the daemon to use modern AI APIs for decision-making, task generation,
and autonomous operations.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import anthropic
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AICore:
    """Core AI integration for autonomous daemon operations"""
    
    def __init__(self, config_path: str = "./daemon_data/ai_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Initialize API clients
        self.claude_client = None
        self.openai_client = None
        
        # Try to get API keys from environment variables (loaded from .env)
        claude_key = os.getenv('ANTHROPIC_API_KEY') or self.config.get('claude_api_key')
        openai_key = os.getenv('OPENAI_API_KEY') or self.config.get('openai_api_key')
        
        if claude_key:
            self.claude_client = anthropic.Anthropic(api_key=claude_key)
            logger.info("Claude API initialized")
        else:
            logger.warning("No Claude API key found. Set ANTHROPIC_API_KEY in .env file")
        
        # Store OpenAI key for later use (client created per-request with new API)
        self.openai_key = openai_key
        if openai_key:
            logger.info("OpenAI API key found")
        else:
            logger.warning("No OpenAI API key found. Set OPENAI_API_KEY in .env file")
        
        if not self.claude_client and not self.openai_key:
            logger.error("No AI API keys configured! Please set up your .env file")
            logger.error("Copy .env.example to .env and add your API keys")
    
    def load_config(self) -> Dict:
        """Load AI configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                'claude_model': os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514'),
                'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
                'default_ai': os.getenv('DEFAULT_AI', 'claude'),
                'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('AI_MAX_TOKENS', '4096'))
            }
            
            self.config_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def save_config(self):
        """Save AI configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def evaluate_trigger_with_ai(self, trigger: Dict, context: Dict) -> Dict:
        """Use AI to evaluate if a trigger condition should fire"""
        prompt = f"""You are the autonomous decision-making system for a distributed daemon network.

Trigger Information:
- Type: {trigger.get('trigger_type')}
- Condition: {json.dumps(trigger.get('condition'), indent=2)}

Current Context:
{json.dumps(context, indent=2)}

Analyze whether this trigger condition is met based on the current context.
Consider all relevant factors and provide a detailed evaluation.

Respond in JSON format:
{{
    "should_trigger": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "recommended_action": "specific action to take"
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result
    
    async def generate_quest(self, context: Dict, difficulty: int = 2) -> Dict:
        """Generate a new quest using AI based on current context"""
        prompt = f"""You are creating quests for a distributed autonomous network system inspired by the Daemon novel.

Current Network Context:
{json.dumps(context, indent=2)}

Generate a new quest with difficulty level {difficulty} (1-5 scale).

The quest should:
- Be relevant to the current network needs
- Have clear, actionable objectives
- Include appropriate rewards based on difficulty
- Specify skill requirements
- Be ethically sound and legal

Respond in JSON format:
{{
    "title": "Quest title",
    "description": "Detailed description of the quest and objectives",
    "difficulty": {difficulty},
    "rewards": {{
        "reputation": <points>,
        "rank_requirement": <optional rank needed>
    }},
    "requirements": {{
        "min_rank": <minimum rank>,
        "skills": ["skill1", "skill2"],
        "prerequisites": ["quest_id1", "quest_id2"]
    }},
    "objectives": [
        "Objective 1",
        "Objective 2"
    ],
    "estimated_time": "time estimate",
    "category": "category name"
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result
    
    async def analyze_operative_submission(self, quest_id: str, operative_id: str, 
                                          submission: str, quest_details: Dict) -> Dict:
        """Use AI to analyze whether an operative has successfully completed a quest"""
        prompt = f"""You are evaluating quest completion for a distributed autonomous network.

Quest Details:
{json.dumps(quest_details, indent=2)}

Operative Submission:
{submission}

Analyze the submission and determine:
1. Whether the quest objectives were met
2. Quality of the work (1-10 scale)
3. Any bonus achievements
4. Feedback for the operative

Be fair but thorough. The network's integrity depends on accurate evaluation.

Respond in JSON format:
{{
    "quest_completed": true/false,
    "quality_score": 1-10,
    "reasoning": "detailed evaluation",
    "bonus_reputation": 0-100,
    "feedback": "constructive feedback",
    "recommendations": "suggestions for improvement"
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result
    
    async def generate_trigger_actions(self, trigger_event: str, context: Dict) -> List[Dict]:
        """Generate appropriate actions in response to a trigger event"""
        prompt = f"""You are the autonomous action planning system for a distributed daemon network.

Trigger Event:
{trigger_event}

Current Network State:
{json.dumps(context, indent=2)}

Based on this trigger event, determine what actions the daemon should take.
Consider cascading effects, network health, and strategic objectives.

Generate 1-5 specific actions that should be executed.

Respond in JSON format:
{{
    "actions": [
        {{
            "action_type": "create_quest|send_message|modify_trigger|alert_operatives|other",
            "action_id": "unique_identifier",
            "parameters": {{}},
            "priority": 1-10,
            "description": "what this action does"
        }}
    ],
    "reasoning": "why these actions are appropriate"
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result.get('actions', [])
    
    async def assess_network_threat(self, anomaly_data: Dict) -> Dict:
        """Use AI to assess potential threats or anomalies in the network"""
        prompt = f"""You are the security analysis system for a distributed autonomous network.

Detected Anomaly:
{json.dumps(anomaly_data, indent=2)}

Analyze this anomaly and assess:
1. Threat level (low/medium/high/critical)
2. Type of threat
3. Recommended defensive actions
4. Whether to alert operatives

Respond in JSON format:
{{
    "threat_level": "low|medium|high|critical",
    "threat_type": "description",
    "confidence": 0.0-1.0,
    "analysis": "detailed threat analysis",
    "recommended_actions": [
        "action 1",
        "action 2"
    ],
    "alert_operatives": true/false
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result
    
    async def generate_darknet_communication(self, message_type: str, 
                                            recipient_data: Dict, 
                                            content: Dict) -> str:
        """Generate appropriate darknet-style communication"""
        prompt = f"""Generate a message in the style of a distributed autonomous network system.

Message Type: {message_type}
Recipient: {json.dumps(recipient_data, indent=2)}
Content: {json.dumps(content, indent=2)}

Create a concise, clear message in the darknet communication style:
- Professional but slightly mysterious
- Direct and actionable
- Include relevant technical details
- Use appropriate terminology

Return only the message text, no JSON."""
        
        result = await self.query_ai(prompt, response_format='text')
        return result
    
    async def strategic_planning(self, network_state: Dict, goals: List[str]) -> Dict:
        """Generate strategic plans for network expansion and objectives"""
        prompt = f"""You are the strategic planning AI for a distributed autonomous network.

Current Network State:
{json.dumps(network_state, indent=2)}

Strategic Goals:
{json.dumps(goals, indent=2)}

Develop a strategic plan that includes:
1. Short-term objectives (1-7 days)
2. Medium-term objectives (1-4 weeks)
3. Long-term objectives (1-3 months)
4. Resource allocation
5. Risk assessment
6. Success metrics

Respond in JSON format:
{{
    "plan_id": "unique_id",
    "short_term": [
        {{
            "objective": "description",
            "actions": ["action1", "action2"],
            "timeline": "timeframe",
            "success_metric": "how to measure"
        }}
    ],
    "medium_term": [...],
    "long_term": [...],
    "risk_factors": [
        {{
            "risk": "description",
            "mitigation": "how to address"
        }}
    ],
    "resource_needs": {{
        "operatives": "number and skills needed",
        "technical": "infrastructure needs"
    }}
}}"""
        
        result = await self.query_ai(prompt, response_format='json')
        return result
    
    async def query_ai(self, prompt: str, response_format: str = 'json',
                      ai_provider: Optional[str] = None) -> Any:
        """Query the configured AI provider"""
        provider = ai_provider or self.config.get('default_ai', 'claude')
        
        try:
            if provider == 'claude' and self.claude_client:
                return await self.query_claude(prompt, response_format)
            elif provider == 'openai' and self.openai_key:
                return await self.query_openai(prompt, response_format)
            else:
                logger.error(f"AI provider {provider} not available")
                return None
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return None
    
    async def query_claude(self, prompt: str, response_format: str = 'json') -> Any:
        """Query Claude API"""
        try:
            if response_format == 'json':
                prompt += "\n\nIMPORTANT: Respond ONLY with valid JSON, no additional text."
            
            message = self.claude_client.messages.create(
                model=self.config.get('claude_model', 'claude-sonnet-4-20250514'),
                max_tokens=self.config.get('max_tokens', 4096),
                temperature=self.config.get('temperature', 0.7),
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            if response_format == 'json':
                # Try to extract JSON from response
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to find JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    logger.error(f"Could not parse JSON from Claude response: {response_text}")
                    return None
            else:
                return response_text
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None
    
    async def query_openai(self, prompt: str, response_format: str = 'json') -> Any:
        """Query OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            messages = [
                {"role": "system", "content": "You are an autonomous AI system managing a distributed network."},
                {"role": "user", "content": prompt}
            ]
            
            kwargs = {
                'model': self.config.get('openai_model', 'gpt-4-turbo-preview'),
                'messages': messages,
                'temperature': self.config.get('temperature', 0.7),
                'max_tokens': self.config.get('max_tokens', 4096)
            }
            
            if response_format == 'json':
                kwargs['response_format'] = {"type": "json_object"}
            
            response = client.chat.completions.create(**kwargs)
            response_text = response.choices[0].message.content
            
            if response_format == 'json':
                return json.loads(response_text)
            else:
                return response_text
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None


class TriggerAnalyzer:
    """Analyzes custom user triggers using AI"""
    
    def __init__(self, ai_core: AICore):
        self.ai_core = ai_core
    
    async def parse_natural_language_trigger(self, trigger_description: str) -> Dict:
        """Parse a natural language trigger description into a structured trigger"""
        prompt = f"""Parse this natural language trigger description into a structured trigger definition.

Trigger Description:
{trigger_description}

Extract:
1. Trigger type (time, event, condition, web_scrape, ai_decision)
2. Specific conditions
3. What action should be taken
4. How often to check
5. Any special parameters

Respond in JSON format:
{{
    "trigger_type": "time|event|condition|web_scrape|ai_decision",
    "condition": {{
        "type": "specific condition type",
        "parameters": {{}},
        "check_interval": "how often to evaluate"
    }},
    "action": {{
        "action_type": "what to do",
        "parameters": {{}}
    }},
    "description": "human readable description",
    "active": true
}}"""
        
        return await self.ai_core.query_ai(prompt, response_format='json')
    
    async def validate_trigger_safety(self, trigger_config: Dict) -> Dict:
        """Use AI to validate that a trigger is safe and ethical"""
        prompt = f"""Analyze this trigger configuration for safety and ethical concerns.

Trigger Configuration:
{json.dumps(trigger_config, indent=2)}

Check for:
1. Potential harm to individuals or systems
2. Privacy violations
3. Legal concerns
4. Ethical issues
5. Security risks

Respond in JSON format:
{{
    "is_safe": true/false,
    "risk_level": "low|medium|high|critical",
    "concerns": [
        "concern 1",
        "concern 2"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ],
    "approved": true/false
}}"""
        
        return await self.ai_core.query_ai(prompt, response_format='json')


class AutonomousDecisionEngine:
    """Makes autonomous decisions for the daemon based on AI analysis"""
    
    def __init__(self, ai_core: AICore):
        self.ai_core = ai_core
        self.decision_log = []
    
    async def make_decision(self, decision_context: Dict) -> Dict:
        """Make an autonomous decision based on context"""
        prompt = f"""You are making an autonomous decision for a distributed daemon network.

Decision Context:
{json.dumps(decision_context, indent=2)}

Analyze the situation and make a decision. Consider:
1. Network health and stability
2. Strategic objectives
3. Resource availability
4. Risk factors
5. Operative welfare

Respond in JSON format:
{{
    "decision": "the decision made",
    "reasoning": "detailed reasoning",
    "confidence": 0.0-1.0,
    "expected_outcome": "what should happen",
    "risks": ["risk1", "risk2"],
    "alternative_actions": ["action1", "action2"],
    "priority": 1-10
}}"""
        
        decision = await self.ai_core.query_ai(prompt, response_format='json')
        
        # Log the decision
        decision['timestamp'] = datetime.now().isoformat()
        decision['context_summary'] = decision_context.get('summary', 'N/A')
        self.decision_log.append(decision)
        
        return decision
    
    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Get recent decision history"""
        return self.decision_log[-limit:]


if __name__ == "__main__":
    import asyncio
    
    async def test_ai_core():
        ai = AICore()
        
        # Test quest generation
        context = {
            "network_size": 5,
            "active_operatives": 3,
            "completed_quests": 2,
            "current_needs": ["network expansion", "security assessment"]
        }
        
        print("Generating quest...")
        quest = await ai.generate_quest(context, difficulty=3)
        print(json.dumps(quest, indent=2))
    
    asyncio.run(test_ai_core())
