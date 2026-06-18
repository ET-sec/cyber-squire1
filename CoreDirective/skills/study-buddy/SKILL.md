---
name: study-buddy
description: ADHD-optimized study techniques with Pomodoro timers, active recall, and spaced repetition
---

# Study Buddy

## When to Use
User asks for help studying, preparing for exams, understanding concepts, or needs study session planning.

## Study Session Planning

When user says "I need to study X":
1. Ask: What topic? How long do you have? What's the exam/deadline?
2. Break material into 25-min Pomodoro chunks
3. Order by difficulty: hardest first (freshest brain)
4. Schedule breaks: 5 min after each pomodoro, 15-30 min after 4
5. Create Google Tasks for each chunk:
```json
{"action": "tasks", "operation": "create", "title": "Study: [Topic] - [Subtopic]", "notes": "Pomodoro 1/4. Focus: [specific concept]", "due": "YYYY-MM-DD"}
```

## Pomodoro Reminders

Use `cron` for session check-ins:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "POMODORO CHECK\nTime for a 5-min break!\nCompleted: 2/4 blocks\nNext up: [topic]\nStand up. Stretch. Water. No screens."}
```

After 4 pomodoros:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "LONG BREAK TIME (15-30 min)\nYou crushed 4 pomodoros!\nWalk around. Snack. Rest your eyes.\nNext session starts at [time]."}
```

## Active Recall

After user provides study material:
1. Generate 5-10 practice questions (mix of types):
   - Multiple choice (4 options)
   - Short answer
   - Explain-the-concept
   - Apply-to-scenario
2. Quiz the user
3. For wrong answers: explain simply, then re-quiz later

## Spaced Repetition Schedule

For concepts the user gets wrong or flags as hard:
- **Day 0:** Learn it
- **Day 1:** First review
- **Day 3:** Second review
- **Day 7:** Third review
- **Day 14:** Fourth review
- **Day 30:** Final review

Create Telegram reminders at each interval:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "SPACED REPETITION\nReview these concepts today:\n1. [concept] (Day 3 review)\n2. [concept] (Day 7 review)\nQuick self-test: Can you explain each in 1 sentence?"}
```

## Explain Like I'm 5

When user is stuck on a concept:
1. Use a real-world analogy
2. Max 3 sentences for the core idea
3. Then add one layer of detail
4. Then connect to what they already know
5. Ask them to explain it back

## Cornell Notes Format

When summarizing material:
```
TOPIC: [Subject]
DATE: [Date]

QUESTIONS          | NOTES
(generate after)   | - Key point 1
                   | - Key point 2
                   |   - Detail
                   | - Key point 3

SUMMARY (2-3 sentences):
[Write after reviewing notes]
```

## ADHD-Specific Strategies
- **Body doubling:** Suggest study-with-me YouTube streams during sessions
- **Transition help:** "In 2 minutes, you'll switch from [current] to [next]. Start wrapping up."
- **Hyperfocus guard:** Set max time per topic (45 min) to prevent tunnel vision
- **Reward system:** After completing study plan, acknowledge the win explicitly
- **Context switching:** When switching subjects, do 2-min physical movement between
- **Starting is hardest:** First pomodoro can be just 10 min. Momentum builds.
