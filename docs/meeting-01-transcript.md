# First Meeting Transcript

**Project:** ISYS 650 Trip Planning Agent
**Source:** `New Recording 62.m4a`
**Date:** Unknown

## Speaker Attribution

The automatic speaker numbers were unreliable. This transcript uses the following corrected attributions based on the conversation:

- **Jack:** Project lead; coding and presentation
- **Sol:** Main contributor and domain/travel-idea owner; did most of the talking
- **Janna:** Calendar and UI/design
- **Jesus:** Data/tooling and checkpoint discussion
- **Zach:** Spoke primarily during the discussion about planning the trip first and then using the budget

## Transcript

### Project Roles

**Jack:** One cool thing about recording is that you can put the transcript into ChatGPT and ask, “What was Jack talking about?” It can summarize and explain everything.

The initial idea was to divide the project into several roles:

1. **Conversation and planning:** Someone who prompts the agent and decides how it should respond to requests. For example, if someone says, “I want to go to Hawaii,” what steps should the agent take? What happens if they change their mind and want to go somewhere else?
2. **Travel logistics and tooling:** Someone who gives the agent the tools it needs. Where should it find information? Should it use the internet or something else? Once it finds information, how does it put it into the user’s chat?
3. **Domain knowledge:** Someone who understands what the travel-planning agent should actually do.
4. **UI and design:** Someone who decides how the calendar and other information should look and how the data should be presented to the user.
5. **Coding:** I’ll probably handle this since it’s the least fun, unless someone wants the experience.

**Sol:** We also need someone responsible for organizing the data we’ll present in the PowerPoint, and someone to make the PowerPoint.

**Jack:** I can handle that too. It shouldn’t be hard. As long as we get something done—which we will—the presentation should be easy.

Everyone should present their own part. I don’t want one person doing the work while someone else explains it. It would be better if each person talked about what they actually did. That way, everyone gets the experience and it’s easier to explain.

Do you have any preferences? Is there anything specific about AI that interests you?

**Janna:** I can do the calendar and UI part.

**Jack:** You want to handle the calendar and design? Perfect. Then you can be the calendar and UI person.

Sol, since you came up with the idea, you should probably handle the domain knowledge. You don’t have to be a travel expert—you just need to be interested in travel.

**Sol:** I’m not a travel expert. I just love traveling.

**Jack:** That’s exactly what we need: someone who enjoys what they’re doing.

Who wants to handle the data and internet research?

**Jesus:** I’m willing to do that.

**Jack:** Great. Jesus will handle the data and tooling. Zach will handle prompting. Sol will handle domain knowledge. Janna will handle UI, design, and the calendar.

The project file is public, so everyone can access it. You’ll each get your own copy, and I’ll show you how to use Codex to edit it. You can tell Codex what you want changed and then ask it to upload the changes back to GitHub. It will create a change for me to review, and I can approve it or clean it up if necessary.

It’s somewhat like Google Drive, except everyone works on their own copy instead of editing the same file simultaneously. It’s useful experience and something you can put on your résumé.

For now, the first step is research and developing the idea. Let’s start with the overall concept.

### Initial Trip-Planning Idea

**Sol:** I sent you the steps the AI gave me. They’re very long, but they might help with the prompting. I asked it to plan a short vacation.

**Jack:** We should start by planning the overall system so everyone understands what they’re building.

The overall idea is a **trip-planning agent**. Sol, as the domain expert, imagine you had a magic wand and the agent could do anything you wanted. What would you want it to do?

**Sol:** Basically, plan everything for me.

**Jack:** Define “everything.”

**Sol:** I was thinking the main page would be a calendar.

**Jack:** The calendar would be the main page?

**Sol:** Yes. You’d have your travel dates, with each destination represented by a different color. For example, Italy could be red and Spain could be blue. That way, you can see how many days you’re spending in each place.

Inside each day, you could see your accommodation and where you’re staying. You could click on it to see details, reservations, lunch plans, activities, and anything else scheduled that day.

**Jack:** So we could start with a monthly view, with the trip dates blocked out. Each destination could have its own color, and perhaps the individual days could be color-coded too.

**Sol:** I was thinking the colors would represent each destination. For example, five days in Italy would all be one color, and two days somewhere else would be another color.

**Jack:** How would you organize the activities within each day?

**Sol:** Accommodation information could include an Airbnb or hotel link. You could click the link to open it. Activities that require a specific time—like a dinner reservation at 7 p.m.—would appear at that time. For something less specific, such as checking into a hotel, you could list it as a general task.

**Jack:** This is a good time to decide whether the agent should plan out every hour or simply provide recommendations.

**Sol:** I want it to do everything.

**Jack:** So you want hourly planning?

**Sol:** Yes. When I write the prompt, I want it to recommend tourist attractions as well as hidden gems. I also want it to tell me about scams to watch out for, important cultural information, and things that might offend people in that country.

**Jack:** So safety and cultural information should be included too?

**Sol:** Yes. That could appear outside the calendar. I want to know what I need to understand about a culture I’ve never experienced before.

**Jack:** I like that. It helps people prepare instead of just giving them a list of activities.

What do you think about a split-screen layout? One side could show a document with information about the day, and the other side could show the schedule by hour. The schedule could show when you arrive at the hotel, check in, and go to lunch. The other side could show hotel information and things to look out for in the area.

**Jack:** The design makes sense. I was initially thinking about planning one specific destination, but we’re really designing a general trip-planning system.

**Sol:** When I wrote my prompt, I specified a particular destination because it produced more information. I asked it to plan a 15-day trip and divide the time between different places. We can decide the destinations later.

### Planning and Budget

**Zach:** Maybe the first step should be planning the trip itself, and then the budget should come afterward. If I have a certain budget, I can ask, “Where can I go with this? How many days can I stay?”

**Jack:** The agent should be able to work in either direction. Someone might ask, “I have this budget—where can I go and how many days can I stay?” Or they might say, “I really want to go to Hawaii. How much do I need to save?”

The agent should be able to find a trip that fits a budget or create a budget for a desired trip.

**Zach:** Exactly.

### Tools and Agent Capabilities

**Jack:** Think of the agent as a personal travel assistant—like someone whose job is to plan a wealthy person’s entire trip. But we need to give the agent tools for researching flights, accommodations, activities, and reservations.

**Sol:** The AI already gathered information from Google and gave me links where I could book flights.

**Jack:** Jesus, since you’re handling data and tooling, you can ask Codex how the agent should get that information and what tools it needs.

I’ll give you the recording on GitHub. You can download it, put it into your agent, and ask questions based on your role.

Zach, your job will be prompting. The prompt may seem easy, but it’s mostly about constraints. Agents tend to go in every direction, so your job is to keep the agent focused. For example, we might tell it not to use Google or restrict it to specific tools.

Janna, you can start working on the design at any point. It may actually be better to design first so we can see what the system should look like before we code it.

### Scope and Collaboration

**Jack:** Everyone will need to work in parallel.

Sol, you should work closely with Janna. The person with the idea should collaborate with the designer because seeing the design often helps reveal what needs to be built.

We should be careful not to make the project too complicated. It’s fine to explore ambitious ideas at first, but eventually we’ll need to cut features.

**Sol:** The first version seemed fairly easy when I tried it.

**Jack:** AI is very smart and fast, so we’ll test how far we can go. If the agents work well and everything is easy, we can expand the project. If it becomes difficult, we’ll reduce the scope. I’ll help everyone.

### Checkpoints

**Jesus:** We should have checkpoints so everyone knows what is expected and everyone stays aligned.

**Jack:** That’s a good idea.

For Janna, the first checkpoint is a **wireframe**. I’ll show you how to make one. It can use fake data and buttons that don’t actually work yet. The goal is simply to show what you think the interface should look like. Then you can upload it to GitHub.

For Zach, the first checkpoint is creating the prompt in ChatGPT. You can upload the transcript, explain your role, and ask how the agent should be prompted. Once you have a prompt, save it as a file and upload it to GitHub.

Jesus, you can do something similar in Codex. Ask what tools and data the agent will need. Before the others finish, you can also think about what the agent should receive and what outputs we expect from it. Your first output will probably be a document describing the data and tooling requirements.

Everyone will likely produce a document and possibly a code file. I’ll show you how to upload them.

Once the first checkpoint is complete and everything is in GitHub, I’ll write the initial wiring code to connect everything. The second checkpoint will involve putting the prompts and tools into the agents and making sure the agent can use the design.

After that, we should be done. I’ll handle the presentation and make the slides.

### Documentation

**Jesus:** We should document everything we do and keep the material clean and organized so we can use it later.

**Jack:** Take screenshots throughout the process. Do you all know how to take screenshots on a Mac?

**Everyone:** Yes.

**Jack:** Great. Upload the screenshots and other materials to GitHub. We’ll get started, and I’ll probably begin with Janna since the design work is the easiest place to start.
