"""
Daemon AI Demonstration Script

This script demonstrates how the modern AI-powered daemon system works,
showing that autonomous systems like those in Suarez's "Daemon" are not only
plausible but trivial to implement with today's AI technology.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from daemon_core import DaemonCore
from ai_integration import AICore
import json
import fade
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

async def demonstrate_ai_capabilities():
    """Demonstrate the AI-powered autonomous capabilities"""
    
    print("=" * 80)
    print("DAEMON NETWORK - AI DEMONSTRATION")
    print("Proving that Daemon-like systems are trivial with modern AI")
    print("=" * 80)
    print()
    
    # Initialize the system
    print("[INIT] Initializing Daemon Core with AI integration...")
    daemon = DaemonCore()
    print(f"[OK] System initialized with {len(daemon.operatives)} operatives\n")
    
    # Check if AI is configured
    if not daemon.ai_core.claude_client and not daemon.ai_core.openai_key:
        print("[WARNING] No AI API keys configured!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables")
        print("See API_SETUP.md for details\n")
        return
    
    if daemon.ai_core.claude_client:
        print("[OK] AI systems operational (Claude)\n")
    elif daemon.ai_core.openai_key:
        print("[OK] AI systems operational (OpenAI)\n")
    
    # Demonstration 1: Natural Language Trigger Creation
    print("-" * 80)
    print("DEMONSTRATION 1: Natural Language Trigger Creation")
    print("-" * 80)
    print()
    
    trigger_examples = [
        "When the network has 5 or more active operatives, automatically generate a challenging group quest",
        "Every day at noon, analyze network performance and create quests based on identified needs",
        "If no quests are completed for 48 hours, create easier introductory quests to re-engage operatives"
    ]
    
    for i, trigger_desc in enumerate(trigger_examples, 1):
        print(f"Example {i}: {trigger_desc}")
        print("Processing with AI...")
        
        trigger_id = await daemon.create_trigger_from_natural_language(trigger_desc)
        
        if trigger_id:
            print(f"[SUCCESS] Trigger created: {trigger_id}")
            print(f"[INFO] The AI has parsed, validated, and activated this trigger")
        else:
            print(f"[REJECTED] AI safety check rejected this trigger")
        print()
    
    # Demonstration 2: AI Quest Generation
    print("-" * 80)
    print("DEMONSTRATION 2: Autonomous Quest Generation")
    print("-" * 80)
    print()
    
    for difficulty in [1, 3, 5]:
        print(f"Generating difficulty {difficulty} quest using AI...")
        quest_id = await daemon.generate_quest_with_ai(difficulty)
        
        if quest_id:
            quest = daemon.quests[quest_id]
            print(f"[SUCCESS] Generated: {quest.title}")
            print(f"  Description: {quest.description}")
            print(f"  Difficulty: {quest.difficulty}")
            print(f"  Rewards: {quest.rewards}")
        print()
    
    # Demonstration 3: AI Decision Making
    print("-" * 80)
    print("DEMONSTRATION 3: Autonomous Decision Making")
    print("-" * 80)
    print()
    
    decision_context = {
        'situation': 'Network activity has dropped by 50% in the last week',
        'options': [
            'Create easier quests to re-engage operatives',
            'Send motivational messages to inactive operatives',
            'Launch a network-wide event',
            'Do nothing and monitor'
        ],
        'network_state': daemon.get_network_context()
    }
    
    print("Decision Context:")
    print(json.dumps(decision_context, indent=2))
    print("\nAsking AI to make autonomous decision...")
    
    decision = await daemon.decision_engine.make_decision(decision_context)
    
    if decision:
        print(f"\n[AI DECISION] {decision.get('decision')}")
        print(f"[REASONING] {decision.get('reasoning')}")
        print(f"[CONFIDENCE] {decision.get('confidence')}")
        print(f"[EXPECTED OUTCOME] {decision.get('expected_outcome')}")
    print()
    
    # Demonstration 4: Trigger Evaluation with AI
    print("-" * 80)
    print("DEMONSTRATION 4: AI Trigger Evaluation")
    print("-" * 80)
    print()
    
    # Create a complex trigger that requires AI reasoning
    complex_trigger = {
        'trigger_id': 'demo_ai_trigger',
        'trigger_type': 'ai_decision',
        'condition': {
            'type': 'complex_analysis',
            'description': 'Evaluate if the network needs intervention based on engagement patterns'
        },
        'action_id': 'generate_intervention_quest'
    }
    
    context = daemon.get_network_context()
    
    print("Evaluating complex trigger with AI:")
    print(json.dumps(complex_trigger, indent=2))
    print("\nNetwork Context:")
    print(json.dumps(context, indent=2))
    print("\nAI Evaluation in progress...")
    
    evaluation = await daemon.ai_core.evaluate_trigger_with_ai(complex_trigger, context)
    
    if evaluation:
        print(f"\n[SHOULD TRIGGER] {evaluation.get('should_trigger')}")
        print(f"[CONFIDENCE] {evaluation.get('confidence')}")
        print(f"[REASONING] {evaluation.get('reasoning')}")
        print(f"[RECOMMENDED ACTION] {evaluation.get('recommended_action')}")
    print()
    
    # Summary
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("KEY TAKEAWAYS:")
    print()
    print("1. AUTONOMOUS TRIGGERS: The system can parse natural language")
    print("   descriptions and create self-executing triggers.")
    print()
    print("2. INTELLIGENT GENERATION: AI creates contextually appropriate")
    print("   quests based on network state and strategic needs.")
    print()
    print("3. AUTONOMOUS DECISIONS: The system can analyze complex situations")
    print("   and make strategic decisions without human oversight.")
    print()
    print("4. SAFETY VALIDATION: AI automatically validates triggers for")
    print("   safety and ethical concerns before activation.")
    print()
    print("This demonstrates that the concepts from 'Daemon' are not science")
    print("fiction - they are trivially implementable with today's AI technology.")
    print()
    print("The only barriers are ethical considerations and human oversight,")
    print("not technical feasibility.")
    print()


async def run_continuous_daemon():
    """Run the daemon in continuous mode with AI monitoring"""
    print("Starting Daemon in continuous autonomous mode...")
    print("Press Ctrl+C to stop\n")
    
    daemon = DaemonCore()
    
    # Generate some initial AI quests if none exist
    if len(daemon.quests) < 3:
        print("Generating initial quests with AI...")
        for difficulty in [1, 2, 3]:
            await daemon.generate_quest_with_ai(difficulty)
        print(f"Generated {len(daemon.quests)} initial quests\n")
    
    # Run the daemon
    try:
        await daemon.run()
    except KeyboardInterrupt:
        print("\nShutting down daemon...")
        daemon.stop()


def main():
    """Main entry point"""
    print("\nDaemon AI System")
    print("=" * 80)
    print()
    print("Choose mode:")
    print("1. Run AI Demonstration (shows AI capabilities)")
    print("2. Run Continuous Daemon (autonomous operation)")
    print("3. Exit")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
    except EOFError:
        choice = "1"  # Default for non-interactive
    
    if choice == "1":
        print()
        asyncio.run(demonstrate_ai_capabilities())
    elif choice == "2":
        print()
        asyncio.run(run_continuous_daemon())
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
