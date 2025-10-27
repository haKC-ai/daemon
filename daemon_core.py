"""
Daemon Core - Main orchestration system inspired by Daemon by Daniel Suarez
This module handles the core daemon logic, trigger monitoring, and task execution.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import secrets
from ai_integration import AICore, TriggerAnalyzer, AutonomousDecisionEngine
import fade
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

banner = r"""
###########+-..           .......++--++#++...      .                   ..-.--....   ... .         ..
##########+++--..           .....--+.#-+++.+..                   ..-.....-.-.....  .......          
####++++-----....            ...-.-+-+++#--...             .     ..--++-+.+--....     ......        
###++##########..             ....--+.#-+...             . . . .....---+-#-+-.........              
####+###+..####..               ...----... .             . .  . . ..-----+--.-........-.............
####+###++-####..   .#######+.     ..+#####-.  ...+###############....+--+#######......+#########-.-
##+-+###+--####..   .#########.  ..-#########. . .+################. ...####++####-....+###+--####.-
+++-+###+..####..     ....+###. ...####..-###.   .+###...###+  ####.   .####..-###-....+###-..####.-
....-###- .####.. . +#########.  ..####. -###.    +###...###+ .####.   .####. -###-.-..-###-..####..
....-###-..####.....####..####. .. ####-.+###. . .+###...###+ .####.   .####. -###-.--.+###-..####.-
....-###-..####.---.###+..+###.. ..##########.....+###. .###+ .####.   .####. -###-.--.+###---####.-
.  .-###-..####.  ..###+ .####.  ..####.... .  .. +###  .###+ .####.   .####..-###-....+###-..####.-
....+###-..####.   .###+..####. ...####-------... +###  .###+ .####.  ..####.--###+-++-+###---####.+
. ..+###-..####.. ..###+..####. .-.####..-###-... +###  .###- .####. . .####..-###+++-.+###-..####..
. ..+#########+.....##########.....-########+.-.. ####  .###- .####.....-#########.--+.+###-..####..
.----+++++++-..-++++--++++++++..-++-.-+##+-...-.. .++-  .+++.  -+++.-+-.-.-++#++---+###+++++++++++-+
..-.-.-.-...   ........    ...    ...           .                .. -. -.--..-.  ... ..------+----+-
"""
print (fade.purplepink(banner))

@dataclass
class Trigger:
    """Represents a trigger condition that activates daemon tasks"""
    trigger_id: str
    trigger_type: str  # 'time', 'event', 'web_scrape', 'condition'
    condition: Dict
    action_id: str
    active: bool = True
    last_checked: Optional[str] = None


@dataclass
class Quest:
    """Represents a quest/task in the daemon system"""
    quest_id: str
    title: str
    description: str
    difficulty: int
    rewards: Dict
    requirements: Dict
    status: str = 'available'  # available, active, completed
    assigned_to: Optional[str] = None


@dataclass
class Operative:
    """Represents a recruited operative in the daemon network"""
    operative_id: str
    username: str
    darknet_name: str
    rank: int
    reputation: int
    skills: List[str]
    completed_quests: List[str]
    active: bool = True
    joined_date: str = None


class DaemonCore:
    """Main daemon orchestration system"""
    
    def __init__(self, data_dir: str = "./daemon_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.triggers: Dict[str, Trigger] = {}
        self.quests: Dict[str, Quest] = {}
        self.operatives: Dict[str, Operative] = {}
        
        self.running = False
        
        # Initialize AI components
        self.ai_core = AICore()
        self.trigger_analyzer = TriggerAnalyzer(self.ai_core)
        self.decision_engine = AutonomousDecisionEngine(self.ai_core)
        logger.info("AI systems initialized")
        
        self.load_state()
        
    def load_state(self):
        """Load daemon state from disk"""
        try:
            if (self.data_dir / "triggers.json").exists():
                with open(self.data_dir / "triggers.json", 'r') as f:
                    data = json.load(f)
                    self.triggers = {k: Trigger(**v) for k, v in data.items()}
                    
            if (self.data_dir / "quests.json").exists():
                with open(self.data_dir / "quests.json", 'r') as f:
                    data = json.load(f)
                    self.quests = {k: Quest(**v) for k, v in data.items()}
                    
            if (self.data_dir / "operatives.json").exists():
                with open(self.data_dir / "operatives.json", 'r') as f:
                    data = json.load(f)
                    self.operatives = {k: Operative(**v) for k, v in data.items()}
                    
            logger.info(f"Loaded state: {len(self.triggers)} triggers, {len(self.quests)} quests, {len(self.operatives)} operatives")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
    
    def save_state(self):
        """Persist daemon state to disk"""
        try:
            with open(self.data_dir / "triggers.json", 'w') as f:
                json.dump({k: asdict(v) for k, v in self.triggers.items()}, f, indent=2)
                
            with open(self.data_dir / "quests.json", 'w') as f:
                json.dump({k: asdict(v) for k, v in self.quests.items()}, f, indent=2)
                
            with open(self.data_dir / "operatives.json", 'w') as f:
                json.dump({k: asdict(v) for k, v in self.operatives.items()}, f, indent=2)
                
            logger.info("State saved successfully")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def create_trigger(self, trigger_type: str, condition: Dict, action_id: str) -> str:
        """Create a new trigger"""
        trigger_id = hashlib.sha256(f"{trigger_type}{datetime.now().isoformat()}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
        
        trigger = Trigger(
            trigger_id=trigger_id,
            trigger_type=trigger_type,
            condition=condition,
            action_id=action_id
        )
        
        self.triggers[trigger_id] = trigger
        self.save_state()
        logger.info(f"Created trigger {trigger_id} of type {trigger_type}")
        return trigger_id
    
    async def create_trigger_from_natural_language(self, description: str) -> Optional[str]:
        """Create a trigger from natural language description using AI"""
        logger.info(f"Parsing natural language trigger: {description}")
        
        # Parse the trigger
        trigger_config = await self.trigger_analyzer.parse_natural_language_trigger(description)
        
        if not trigger_config:
            logger.error("Failed to parse trigger")
            return None
        
        # Validate safety
        safety_check = await self.trigger_analyzer.validate_trigger_safety(trigger_config)
        
        if not safety_check.get('approved', False):
            logger.warning(f"Trigger rejected due to safety concerns: {safety_check.get('concerns')}")
            return None
        
        # Create the trigger
        trigger_id = self.create_trigger(
            trigger_type=trigger_config['trigger_type'],
            condition=trigger_config['condition'],
            action_id=trigger_config['action'].get('action_type', 'ai_decision')
        )
        
        # Store the full AI-parsed config for reference
        trigger_config_file = self.data_dir / f"trigger_{trigger_id}_config.json"
        with open(trigger_config_file, 'w') as f:
            json.dump(trigger_config, f, indent=2)
        
        logger.info(f"Created AI-powered trigger {trigger_id}")
        return trigger_id
    
    def create_quest(self, title: str, description: str, difficulty: int, rewards: Dict, requirements: Dict) -> str:
        """Create a new quest"""
        quest_id = hashlib.sha256(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            difficulty=difficulty,
            rewards=rewards,
            requirements=requirements
        )
        
        self.quests[quest_id] = quest
        self.save_state()
        logger.info(f"Created quest: {title}")
        return quest_id
    
    async def generate_quest_with_ai(self, difficulty: int = 2) -> Optional[str]:
        """Generate a new quest using AI based on network context"""
        context = {
            'network_size': len(self.operatives),
            'active_operatives': sum(1 for op in self.operatives.values() if op.active),
            'completed_quests': sum(1 for q in self.quests.values() if q.status == 'completed'),
            'active_quests': sum(1 for q in self.quests.values() if q.status == 'active'),
            'average_rank': sum(op.rank for op in self.operatives.values()) / max(len(self.operatives), 1),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generating AI quest with difficulty {difficulty}")
        quest_data = await self.ai_core.generate_quest(context, difficulty)
        
        if not quest_data:
            logger.error("Failed to generate quest")
            return None
        
        quest_id = self.create_quest(
            title=quest_data.get('title', 'Untitled Quest'),
            description=quest_data.get('description', ''),
            difficulty=quest_data.get('difficulty', difficulty),
            rewards=quest_data.get('rewards', {'reputation': 50}),
            requirements=quest_data.get('requirements', {'min_rank': 1})
        )
        
        logger.info(f"AI generated quest: {quest_data.get('title')}")
        return quest_id
    
    def recruit_operative(self, username: str, skills: List[str]) -> str:
        """Recruit a new operative into the daemon network"""
        operative_id = hashlib.sha256(f"{username}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        darknet_name = self.generate_darknet_name()
        
        operative = Operative(
            operative_id=operative_id,
            username=username,
            darknet_name=darknet_name,
            rank=1,
            reputation=0,
            skills=skills,
            completed_quests=[],
            joined_date=datetime.now().isoformat()
        )
        
        self.operatives[operative_id] = operative
        self.save_state()
        logger.info(f"Recruited operative: {username} (darknet: {darknet_name})")
        return operative_id
    
    def generate_darknet_name(self) -> str:
        """Generate a darknet pseudonym for an operative"""
        prefixes = ['Shadow', 'Ghost', 'Cipher', 'Raven', 'Phantom', 'Void', 'Nexus']
        suffixes = ['Walker', 'Runner', 'Seeker', 'Hunter', 'Weaver', 'Breaker', 'Keeper']
        return f"{secrets.choice(prefixes)}{secrets.choice(suffixes)}{secrets.randbelow(999):03d}"
    
    def assign_quest(self, quest_id: str, operative_id: str) -> bool:
        """Assign a quest to an operative"""
        if quest_id not in self.quests or operative_id not in self.operatives:
            return False
            
        quest = self.quests[quest_id]
        operative = self.operatives[operative_id]
        
        # Check if operative meets requirements
        if quest.requirements.get('min_rank', 0) > operative.rank:
            logger.warning(f"Operative {operative.darknet_name} does not meet rank requirement")
            return False
        
        quest.status = 'active'
        quest.assigned_to = operative_id
        self.save_state()
        
        logger.info(f"Assigned quest '{quest.title}' to {operative.darknet_name}")
        return True
    
    def complete_quest(self, quest_id: str, operative_id: str) -> bool:
        """Mark a quest as completed and grant rewards"""
        if quest_id not in self.quests or operative_id not in self.operatives:
            return False
            
        quest = self.quests[quest_id]
        operative = self.operatives[operative_id]
        
        if quest.assigned_to != operative_id:
            return False
        
        quest.status = 'completed'
        operative.completed_quests.append(quest_id)
        operative.reputation += quest.rewards.get('reputation', 0)
        
        # Level up logic
        if operative.reputation >= operative.rank * 100:
            operative.rank += 1
            logger.info(f"{operative.darknet_name} leveled up to rank {operative.rank}")
        
        self.save_state()
        logger.info(f"Quest '{quest.title}' completed by {operative.darknet_name}")
        return True
    
    async def check_triggers(self):
        """Check all active triggers and execute actions if conditions are met"""
        for trigger_id, trigger in self.triggers.items():
            if not trigger.active:
                continue
                
            try:
                trigger.last_checked = datetime.now().isoformat()
                should_fire = False
                
                if trigger.trigger_type == 'time':
                    should_fire = self.check_time_condition(trigger.condition)
                        
                elif trigger.trigger_type == 'event':
                    should_fire = self.check_event_condition(trigger.condition)
                        
                elif trigger.trigger_type == 'condition':
                    should_fire = self.check_general_condition(trigger.condition)
                
                elif trigger.trigger_type == 'ai_decision':
                    # Use AI to evaluate complex conditions
                    context = self.get_network_context()
                    ai_evaluation = await self.ai_core.evaluate_trigger_with_ai(
                        asdict(trigger), 
                        context
                    )
                    if ai_evaluation:
                        should_fire = ai_evaluation.get('should_trigger', False)
                        logger.info(f"AI evaluation for trigger {trigger_id}: {ai_evaluation.get('reasoning')}")
                
                if should_fire:
                    await self.execute_action(trigger.action_id, trigger_id)
                        
            except Exception as e:
                logger.error(f"Error checking trigger {trigger_id}: {e}")
    
    def get_network_context(self) -> Dict:
        """Get current network context for AI decision making"""
        return {
            'total_operatives': len(self.operatives),
            'active_operatives': sum(1 for op in self.operatives.values() if op.active),
            'total_quests': len(self.quests),
            'available_quests': sum(1 for q in self.quests.values() if q.status == 'available'),
            'active_quests': sum(1 for q in self.quests.values() if q.status == 'active'),
            'completed_quests': sum(1 for q in self.quests.values() if q.status == 'completed'),
            'average_rank': sum(op.rank for op in self.operatives.values()) / max(len(self.operatives), 1),
            'total_reputation': sum(op.reputation for op in self.operatives.values()),
            'active_triggers': sum(1 for t in self.triggers.values() if t.active),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_time_condition(self, condition: Dict) -> bool:
        """Check if time condition is met"""
        target_time = condition.get('time')
        if not target_time:
            return False
        return datetime.now().strftime('%H:%M') == target_time
    
    def check_event_condition(self, condition: Dict) -> bool:
        """Check if event condition is met"""
        event_file = self.data_dir / "events.json"
        if not event_file.exists():
            return False
            
        with open(event_file, 'r') as f:
            events = json.load(f)
            
        event_type = condition.get('event_type')
        return any(e.get('type') == event_type for e in events)
    
    def check_general_condition(self, condition: Dict) -> bool:
        """Check general condition"""
        condition_type = condition.get('type')
        
        if condition_type == 'operative_count':
            return len(self.operatives) >= condition.get('threshold', 0)
        elif condition_type == 'quest_completion':
            completed = sum(1 for q in self.quests.values() if q.status == 'completed')
            return completed >= condition.get('threshold', 0)
            
        return False
    
    async def execute_action(self, action_id: str, trigger_id: Optional[str] = None):
        """Execute an action triggered by a condition"""
        logger.info(f"Executing action: {action_id}")
        
        # Get network context
        context = self.get_network_context()
        
        # Use AI to determine appropriate actions
        trigger_event = f"Action {action_id} triggered"
        if trigger_id:
            trigger_event += f" by trigger {trigger_id}"
        
        actions = await self.ai_core.generate_trigger_actions(trigger_event, context)
        
        # Execute each action
        for action in actions:
            action_type = action.get('action_type')
            
            if action_type == 'create_quest':
                difficulty = action.get('parameters', {}).get('difficulty', 2)
                await self.generate_quest_with_ai(difficulty)
            
            elif action_type == 'send_message':
                # Log message action
                logger.info(f"Message action: {action.get('description')}")
            
            elif action_type == 'modify_trigger':
                # Modify trigger state
                target_trigger = action.get('parameters', {}).get('trigger_id')
                if target_trigger in self.triggers:
                    self.triggers[target_trigger].active = action.get('parameters', {}).get('active', True)
            
            elif action_type == 'alert_operatives':
                # Alert system
                logger.info(f"Alert: {action.get('description')}")
        
        # Log the action
        action_log = {
            'action_id': action_id,
            'trigger_id': trigger_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'executed',
            'ai_generated_actions': actions
        }
        
        log_file = self.data_dir / "action_log.json"
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(action_log)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        self.save_state()
    
    async def run(self):
        """Main daemon loop"""
        self.running = True
        logger.info("Daemon core started")
        
        try:
            while self.running:
                await self.check_triggers()
                await asyncio.sleep(5)  # Check every 5 seconds
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        finally:
            self.save_state()
            logger.info("Daemon core stopped")
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        self.save_state()


if __name__ == "__main__":
    # Initialize and run daemon
    daemon = DaemonCore()
    
    # Create some initial content
    if not daemon.quests:
        daemon.create_quest(
            title="First Contact",
            description="Complete the initialization protocol and prove your worth.",
            difficulty=1,
            rewards={'reputation': 50},
            requirements={'min_rank': 1}
        )
        
        daemon.create_quest(
            title="Network Infiltration",
            description="Gain access to restricted network segments.",
            difficulty=3,
            rewards={'reputation': 150},
            requirements={'min_rank': 2}
        )
    
    # Run the daemon
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        logger.info("Daemon shutdown requested")
        daemon.stop()
