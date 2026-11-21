# Batch Processing in D365 F&O: RunBaseBatch vs. SysOperation — From Restaurant Orders to Production Batch Jobs

## Before We Talk About Code, Let's Go to a Restaurant

Imagine you walk into a busy restaurant. You are hungry. You walk to the counter and say:

> “I'd like a chicken sandwich.”

The person at the counter takes your order. The kitchen starts preparing it. You stand there. You wait. You watch the chef work. A few minutes later:

> “Order 27!”

You take your sandwich and leave.

Simple.

Now imagine the restaurant gets busy. There are 100 customers. Then 500. Then 5,000. Would the restaurant still ask every customer to stand at the kitchen counter and wait while their food is prepared?

Of course not.

Instead, the restaurant introduces a **queue**. You place your order. Your order is recorded. You receive an order number. You walk away. The kitchen picks up the next available order. The cooks prepare it. When it is finished, the order is marked complete. You can come back and check its status.

Now something interesting has happened. The restaurant has separated two things: **Ordering the food** from **Preparing the food**.

And that is the first idea behind batch processing in D365 F&O.

---

# 1. Your User Session Is the Customer at the Counter

Let's bring our Sales Order requirement into the restaurant.

Your user opens your Sales Order Invoice process. They select **SO001**, **SO002**, and **SO003**.

The user has essentially walked up to the restaurant counter and said:

> “These are the orders I want processed.”

Now imagine if the user had to stand there while D365 did this:

**SO001 → Confirm → Packing Slip → Invoice**

then:

**SO002 → Confirm → Packing Slip → Invoice**

then:

**SO003 → Confirm → Packing Slip → Invoice**

For three Sales Orders, perhaps nobody cares. But what if there are 300? Or 3,000? Or the process takes 45 minutes?

The user is now effectively standing at the counter watching the chef cook 3,000 sandwiches. That is not a great ERP experience.

This is where batch processing changes the relationship.

Instead of saying:

> “Stay here while I process everything.”

the system can say:

> “Your work has been placed in the queue. You can go.”

That is the fundamental value of batch processing.

---

# 2. So What Exactly Is the Queue?

Now let's replace the restaurant terminology with D365 terminology.

The restaurant has:

**Customer → places an order**

**Order ticket → records what needs to be done**

**Kitchen → performs the work**

**Kitchen staff → processes the queued orders**

**Completed order → tells us the work is finished**

D365 has roughly the same conceptual structure:

**User → submits an operation**

**Batch Job / Batch Task → represents queued work**

**Batch Server → executes the work**

**X++ business logic → performs the operation**

**Batch history/status → tells us what happened**

So when you hear:

> “This needs to run as a batch job.”

don't immediately think:

> “I need to extend a certain class.”

Think first:

> **“I need to take this work out of the user's immediate session and give it to the background processing system.”**

That mental model will take you much further.

---

# 3. But There Is a Second Problem

Our restaurant is now successful. Customers don't have to stand at the counter anymore. But the restaurant still needs a system for **how orders are written down and organized**.

And this is where things get interesting.

Imagine two restaurants. Both have the same kitchen. Both prepare the same food. Both have the same number of cooks. But they organize orders differently.

### Restaurant A

One employee handles everything. They take the customer's order, write it down, keep track of it, send it to the kitchen, check the status, organize the paperwork, and tell the customer when it is finished.

### Restaurant B

The restaurant has specialized roles. One person takes the order. Another manages the order information. Another coordinates the kitchen. The kitchen staff focuses purely on preparing the food.

Both restaurants can produce the same chicken sandwich. But which restaurant's process is easier to expand when the business becomes huge?

That is the difference we are about to see between **RunBaseBatch and SysOperation**.

---

# 4. Meet RunBaseBatch: The One-Person Restaurant

Let's look at the RunBase implementation we created:

`VSISalesOrderInvoiceRunBase`

Look inside it.

Who builds the dialog? The class does. Who gets the selected Sales Orders? The class does. Who validates the selection? The class does. Who remembers the parameters? The class does. Who packs the parameters? The class does. Who restores them? The class does. Who processes the Sales Orders? The class does. Who confirms them? The class does. Who posts the packing slip? The class does. Who posts the invoice? The class does.

You can almost imagine one restaurant employee saying:

> “Don't worry. I'll take the order, write the ticket, store the ticket, find the ticket later, cook the food, serve it, and close the order.”

That is RunBase.

It is an **all-in-one approach**.

And before we criticize it, notice something important. It is actually quite convenient.

---

# 5. Why Would Anyone Want the One-Person Restaurant?

Imagine your restaurant only serves 20 customers a day. Do you really need an order manager, a kitchen manager, a dispatcher, a cashier, a dedicated ticketing system, and a separate operations department?

Probably not.

You might actually prefer:

> “Give me one capable person who can handle the whole thing.”

That is one of RunBase's strengths.

For a small, self-contained operation, the model is straightforward. You open the class and follow the flow.

In our implementation, you can almost read the class like a story:

**Open dialog → Select Sales Orders → Validate → Save parameters → Run → Find Sales Order → Confirm → Packing Slip → Invoice**

That directness is valuable.

So don't fall into the beginner's trap of saying:

> “RunBase is old, therefore RunBase is bad.”

That is not the lesson.

RunBase is mature, established, and still present throughout D365 F&O.

The real question is:

> **What happens when our restaurant becomes much larger?**

---

# 6. The Restaurant Has a Ticket — But Who Keeps It?

Now imagine the customer places an order and walks away.

The employee has written:

> “Chicken sandwich — Order 27.”

But the employee isn't going to stand there forever. The restaurant needs to preserve that information.

This is where our RunBase code introduces something that might initially look strange:

`pack()`

and

`unpack()`.

Think of `pack()` as putting the order ticket into a secure envelope before the employee leaves.

The ticket says:

> “This job needs these Sales Orders.”

The system stores that information. Later, when the batch server picks up the job, a new instance can reconstruct the required state.

That's the idea behind:

**pack → persist → unpack → run**

This is an important concept because batch processing is not simply:

> “Keep this object alive and call `run()` later.”

The system needs a durable representation of the job's state.

---

# 7. And Why Do We Need a Version?

Now imagine the restaurant changes its order ticket.

Yesterday the ticket said:

> Order number

Today it says:

> Order number + delivery address

Tomorrow:

> Order number + delivery address + allergy information

What happens to yesterday's tickets?

The restaurant needs to know which version of the ticket it is looking at.

That's why our RunBase class uses:

`CurrentVersion`

and:

`CurrentList`

The version tells the class:

> “This stored state belongs to this version of the class structure.”

This is why `pack()` and `unpack()` aren't just annoying boilerplate. They teach you something fundamental about batch development:

> **A batch job may execute later than the moment it was submitted, so its required state must be safely persisted and reconstructable.**

That is a production concept, not merely a framework trick.

---

# 8. Now Our Restaurant Gets Bigger

The restaurant is successful. We now have 10,000 orders. The one employee is becoming overwhelmed.

Management says:

> “We need a better organization.”

And this is where SysOperation enters the story.

Instead of giving one person the entire backpack, we split the responsibilities.

---

# 9. SysOperation: The Restaurant Becomes a Team

Look at our SysOperation implementation.

We have:

**Contract**

**UI Builder**

**Service**

**Controller**

At first, a trainee might look at that and say:

> “Why did we need four classes for something RunBase handled in one?”

That's actually a very good question.

Because SysOperation is deliberately changing the architecture.

Instead of:

> **“One class handles everything.”**

we move toward:

> **“Each part of the operation has a responsibility.”**

Think of our restaurant again.

---

# 10. The Contract Is the Order Ticket

The first person asks:

> “What did the customer actually order?”

That's our **Data Contract**.

In our implementation, the contract contains:

**Sales Orders**

The contract is not responsible for confirming the Sales Order. It doesn't post the packing slip. It doesn't post the invoice.

It simply says:

> “Here is the information this operation needs.”

That is its job.

This gives us a clean boundary.

The business operation can say:

> “Give me the information I need.”

without caring about how the user entered it.

---

# 11. The UI Builder Is the Waiter Taking the Order

Now who interacts with the customer?

The waiter.

In our application, that's conceptually what the UI Builder is doing.

The user doesn't type some mysterious comma-separated string into a box and hope for the best.

Our UI Builder creates the Sales Order lookup. It filters the Sales Orders. It shows the appropriate records. It gives the user a multi-select experience.

The user says:

> “I want these Sales Orders.”

The UI Builder handles that interaction.

Notice what has happened.

The person taking the order doesn't need to cook the food.

That is exactly the point.

---

# 12. The Service Is the Kitchen

Now we finally arrive at the most important class:

`VSISalesOrderInvoiceService`

This is where the actual work happens.

The service receives the selected Sales Orders. Then it says:

> “Okay. Let's process them.”

For each Sales Order, it performs the business process:

**Find Sales Order → Check status → Confirm → Post packing slip → Post invoice**

The kitchen doesn't care whether the customer ordered from a waiter, an app, a phone call, a website, or a kiosk.

The kitchen's job is:

> **Prepare the food.**

Likewise, the service's job is:

> **Perform the business operation.**

That separation is one of the biggest architectural advantages of SysOperation.

---

# 13. And Then We Have the Controller

Someone still needs to tell the restaurant:

> “Start processing this order.”

That's where the **Controller** comes in.

Our:

`VSISalesOrderInvoiceController`

connects the framework pieces.

It knows:

> “Which service should I call?”

> “Which method should I execute?”

> “How should this operation execute?”

That last question is especially important.

Because now we reach one of the most misunderstood concepts in SysOperation.

---

# 14. SysOperation Is Not Automatically Batch

Imagine the restaurant has two choices.

### Option 1

The chef starts cooking immediately while you wait.

### Option 2

The order goes onto the kitchen queue and the kitchen processes it in the background.

Those are two different execution behaviors.

SysOperation provides the structure for the operation. The **execution mode** determines how the operation runs.

Our current controller explicitly uses:

`SysOperationExecutionMode::Synchronous`

So our current implementation is effectively saying:

> “Start the kitchen operation now, and let the user wait for the result.”

That is SysOperation.

But it isn't necessarily scheduled batch execution.

This distinction is worth remembering:

> **SysOperation is a framework. Batch is an execution model.**

SysOperation can participate in batch execution, but the two terms are not interchangeable.

---

# 15. Now Change One Thing

Suppose management says:

> “Don't make the user wait. Put this Sales Order process into the kitchen queue.”

Now we move toward a scheduled batch execution model.

The architecture doesn't need to become a completely different business process. The same general idea remains:

**Contract → Service → Controller → Batch execution**

That is powerful.

The kitchen is still the kitchen.

We are simply changing **how the order gets to the kitchen**.

---

# 16. So What Did We Actually Gain?

This is the question you should always ask when learning a framework.

Not:

> “What classes did Microsoft create?”

But:

> **“What did I gain by using them?”**

With SysOperation, we gained separation.

The contract owns the parameters. The UI owns the interaction. The service owns the business logic. The controller owns the execution setup.

That means if the UI changes tomorrow, we don't necessarily need to rewrite the business logic. If the execution method changes, the service does not necessarily need to change. If the service logic needs to be tested, we don't need to reproduce the entire dialog.

The restaurant has become easier to organize because everyone knows their job.

---

# 17. This Is Why SysOperation Became the Preferred Pattern

Now the reason becomes much easier to understand.

Microsoft didn't move toward SysOperation simply because:

> “RunBase is old.”

The deeper reason is architectural.

Modern enterprise applications need:

**Separation of concerns**

**Maintainability**

**Reusability**

**Extensibility**

**Testability**

**Structured parameter handling**

SysOperation naturally supports those ideas.

RunBase can still accomplish many of them, but you as the developer carry more of that responsibility yourself.

So the evolution looks something like this:

### RunBase thinking

> “Here is my class. It knows how to do everything.”

### SysOperation thinking

> “Here is my operation. Different parts of the application have different responsibilities.”

That is a much more important lesson than simply memorizing framework names.

---

# 18. But Our Restaurant Has Another Problem

We solved one problem. Customers don't have to wait at the counter.

But now the kitchen receives:

**10,000 orders.**

One chef processes:

**Order 1 → Order 2 → Order 3 → Order 4 → Order 5 → ...**

This could still take forever.

And this is where trainees often make another mistake.

They think:

> “It's a batch job, so it must be running in parallel.”

No.

Batch does not automatically mean parallel.

Our current Sales Order service contains a loop. Conceptually it says:

> “Take the first Sales Order and process it. Then take the next one.”

That is sequential work.

Putting the loop into a batch job changes **where/how it executes**, not automatically **how many pieces execute simultaneously**.

---

# 19. Now Imagine the Restaurant Adds More Chefs

Management says:

> “We have 10,000 orders. Give me five chefs.”

Now we have parallel processing.

**Chef 1 → Orders 1–2,000**

**Chef 2 → Orders 2,001–4,000**

**Chef 3 → Orders 4,001–6,000**

**Chef 4 → Orders 6,001–8,000**

**Chef 5 → Orders 8,001–10,000**

Now the restaurant is faster.

But another problem appears.

What if Chef 1 and Chef 2 both grab Order 25?

Now we have duplicate work.

The restaurant needs a way to say:

> “This order has already been claimed.”

And that is where production-grade batch design becomes much more interesting.

---

# 20. The Real Production Questions Begin Here

When your batch job becomes large, you start asking questions such as:

> Who owns this piece of work?

> Has somebody already processed it?

> What happens if processing fails?

> Can we retry it?

> How do we know what succeeded?

> What happens if the batch server crashes?

> How many workers should run simultaneously?

> Are multiple workers locking the same records?

> Should everything be inside one transaction?

These are not really RunBase-vs-SysOperation questions anymore.

They are **batch architecture questions**.

And this distinction is important.

Choosing SysOperation does not magically solve scalability.

It gives you a cleaner foundation from which you can build a scalable solution.

---

# 21. One Giant Restaurant Order vs. Individual Orders

Suppose we process 10,000 Sales Orders in one giant transaction.

Chef starts:

**SO001 → ... → SO9999 → ... → SO10000**

Then SO10,000 fails.

What happens?

If everything was part of one transaction, we could potentially roll back the entire operation.

Now imagine the manager hearing:

> “Sorry, 9,999 orders were successfully processed, but because the last one failed, everything has been rolled back.”

That's terrible operationally.

A better production design usually thinks in terms of **small, independent units of work**.

For example:

**SO001 → commit**

**SO002 → commit**

**SO003 → commit**

If SO004 fails:

**SO001 → Done**

**SO002 → Done**

**SO003 → Done**

**SO004 → Error**

Now SO005 can potentially continue.

This is where transaction design and retry design become extremely important.

---

# 22. The Batch Server Becomes the Kitchen Manager

Now zoom out.

The restaurant isn't just one kitchen anymore. It has multiple chefs, multiple orders, priorities, queues, failures, retries, schedules, and customers waiting for results.

This is much closer to what a production D365 environment looks like.

The batch infrastructure manages queued work. Batch groups can influence where work is processed. Concurrency controls how much work a batch server handles. Priority influences which ready work gets attention. Recurrence allows jobs to come back automatically. History allows administrators to investigate what happened.

The business code still has to be written correctly.

But now the platform gives you an infrastructure for operating that code at scale.

---

# 23. So Why Keep RunBase Around?

Now our answer should be obvious.

Imagine the restaurant has thousands of old recipes. They work. The staff knows them. Customers are happy.

You wouldn't throw away every recipe just because the restaurant hired a new management system.

That's effectively the situation with RunBase.

D365 F&O contains a huge amount of established functionality. Rewriting working code simply because a newer framework exists would introduce unnecessary risk.

So RunBase remains important because:

**Existing systems use it.**

**Existing customizations use it.**

**Developers still need to maintain it.**

**It is proven and mature.**

The lesson isn't:

> “Forget RunBase.”

The lesson is:

> **“Understand RunBase well enough to maintain the past, and understand SysOperation well enough to build the future.”**

---

# 24. The Two Restaurants Are Still Using the Same Kitchen

And here's perhaps the most important point.

Don't imagine RunBase and SysOperation as two completely different batch engines.

They aren't two different kitchens.

They are two different ways of **organizing the order before it reaches the kitchen**.

Once work is submitted as a batch job, the underlying D365 batch infrastructure is responsible for executing that queued work.

So the distinction is primarily at the **application/framework design level**.

RunBase says:

> “I'll package my operation this way.”

SysOperation says:

> “I'll structure my operation this way.”

The batch infrastructure then executes the work.

This is why saying:

> “SysOperation batch jobs are faster than RunBase batch jobs.”

is not a good general statement.

The framework itself isn't what magically makes the business operation faster.

The workload design, query efficiency, transaction boundaries, locking, task distribution, and concurrency strategy matter enormously.

---

# 25. The Restaurant Story in One Picture

You can now mentally map the entire concept:

**Customer → User**

**Order → Business operation**

**Order ticket → Parameters / contract**

**Waiter → UI**

**Kitchen → Service / business logic**

**Kitchen manager → Controller / execution orchestration**

**Kitchen queue → Batch infrastructure**

**Chef → Batch worker**

**Multiple chefs → Parallel batch tasks**

**Order status → Batch status / processing status**

**Failed order → Error / retry scenario**

And suddenly a collection of unfamiliar D365 terms becomes a system you can visualize.

That is exactly what a good mental model should do.

---

# 26. What Should a New D365 Developer Remember?

Don't leave this topic thinking:

> “RunBase has `pack()` and SysOperation has a Contract.”

That's too shallow.

Leave thinking:

### RunBaseBatch

**Simple, direct, mature, and useful for existing or straightforward operations.**

You get a compact model, but you take responsibility for more of the plumbing.

### SysOperation

**Structured, separated, reusable, and better aligned with modern development.**

You write more classes, but each class has a clearer responsibility.

### Batch

**A way of executing work in the background through the D365 batch infrastructure.**

It doesn't automatically mean parallel processing.

### Production batch design

**The real challenge is making the workload reliable, scalable, retryable, and observable.**

That is where senior-level thinking begins.

---

# 27. And Here Is the Interview Question That Catches People

Imagine you're sitting in a D365 F&O technical interview.

The interviewer asks:

> **“What is the difference between RunBaseBatch and SysOperation?”**

The beginner answer is:

> “RunBaseBatch is old and SysOperation is new.”

That's not a strong answer.

A better answer is:

> **“RunBaseBatch and SysOperation are different application frameworks for structuring operations that can be executed through the D365 batch infrastructure. RunBaseBatch typically combines dialog handling, parameter state, serialization, validation, and execution in one class, using methods such as** **`dialog()`****,** **`pack()`****, **`unpack()`****, and** **`run()`****. SysOperation separates these responsibilities through concepts such as Data Contracts, Services, and Controllers. SysOperation is generally preferred for new development because it provides cleaner separation of concerns, stronger parameter modeling, better reuse, and a better foundation for maintainability and extensibility.”**

But then comes the **follow-up question that separates someone who memorized the answer from someone who actually understands it:**

> **“Does SysOperation always run as a batch job?”**

The correct answer:

> **“No. SysOperation is a framework, not synonymous with batch. Its controller can specify different execution modes. Batch execution is one of those modes.”**

And then the interviewer may push further:

> **“If both RunBaseBatch and SysOperation ultimately use the batch infrastructure, why would you choose SysOperation?”**

Now you have the real answer:

> **“Primarily because of architecture, not because the batch engine is fundamentally different. SysOperation separates parameters, UI, orchestration, and business logic, making new functionality easier to maintain, test, reuse, and extend.”**

And if the interviewer asks one final question:

> **“Does using SysOperation automatically make a batch job scalable?”**

Your answer should be:

> **“No. Scalability depends on how the workload is designed — task partitioning, concurrency, transaction boundaries, locking, query performance, retry behavior, and the size of each unit of work. The framework provides the structure, but the developer still has to design the workload correctly.”**

That last answer is the one worth remembering.

Because at that point, you are no longer just telling the interviewer what a framework is.

You are demonstrating that you understand **why it exists, what problem it solves, and what problems it does not solve.**

---

# Final Thought

The restaurant analogy was never really about restaurants.

It was about changing the way you think about enterprise software.

A beginner thinks:

> **“I have code that needs to run.”**

A batch developer thinks:

> **“I have work that needs to be queued and executed safely.”**

A stronger D365 developer thinks:

> **“I need to design how that work is represented, executed, monitored, retried, and scaled.”**

And an experienced developer asks one level deeper:

> **“What architecture will allow this business process to keep working when the number of users, records, failures, and executions becomes 100 times larger than it is today?”**

That is the real journey from understanding `RunBaseBatch` and `SysOperation` to understanding **batch processing in D365 F&O**.
