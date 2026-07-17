# Refactoring Techniques — Execution Reference

Sixty-one named techniques, grouped by purpose. Each entry gives the intent,
when to reach for it, and a safe step sequence. The steps are one proven
path, not the only one: take larger strides while everything stays green,
and fall back to exactly these small steps the moment something breaks.
**Every step ends with running the tests** — that clause is omitted below
only to avoid repeating it sixty-one times.

Many techniques come in inverse pairs (extract/inline, pull up/push down).
The inverse is noted where it exists; apply whichever direction moves the
code toward the structure the current change needs.

This file is built for lookup, not linear reading: find the technique in
the index below, then locate its `### <Name>` heading and read that entry
alone.

## Index

**Foundations**

| Technique | Essence | Pairs with |
|---|---|---|
| Extract Function | Fragment → function named for its purpose | Inline Function |
| Inline Function | Collapse needless indirection | Extract Function |
| Extract Variable | Name a subexpression | Inline Variable |
| Inline Variable | Remove a name that adds nothing | Extract Variable |
| Change Function Declaration | Rename or reshape a signature | — |
| Encapsulate Variable | Route data access through functions | — |
| Rename Variable | Make a name say what it holds | — |
| Introduce Parameter Object | Group values that travel together | — |
| Combine Functions into Class | Bind functions to their shared data | Combine Functions into Transform |
| Combine Functions into Transform | Enriched copy carries all derivations | Combine Functions into Class |
| Split Phase | Two sequential concerns → two phases | — |

**Encapsulation**

| Technique | Essence | Pairs with |
|---|---|---|
| Encapsulate Record | Bare record → class | — |
| Encapsulate Collection | Guard the underlying collection | — |
| Replace Primitive with Object | Grow a domain type from a bare value | — |
| Replace Temp with Query | Temp variable → shared function | — |
| Extract Class | Split a two-job class | Inline Class |
| Inline Class | Fold a fading class into its user | Extract Class |
| Hide Delegate | Stop client hop-navigation | Remove Middle Man |
| Remove Middle Man | Drop a wall of forwarders | Hide Delegate |
| Substitute Algorithm | Swap in a clearer algorithm | — |

**Moving features**

| Technique | Essence | Pairs with |
|---|---|---|
| Move Function | Put it with the data it uses | — |
| Move Field | Move data to its true home | — |
| Move Statements into Function | Absorb always-adjacent statements | Move Statements to Callers |
| Move Statements to Callers | Push diverging work to the boundary | Move Statements into Function |
| Replace Inline Code with Function Call | Call the function that already exists | — |
| Slide Statements | Bring related lines together | — |
| Split Loop | One loop per job | — |
| Replace Loop with Pipeline | Loop → filter/map chain | — |
| Remove Dead Code | Delete the unused | — |

**Organizing data**

| Technique | Essence | Pairs with |
|---|---|---|
| Split Variable | One variable per meaning | — |
| Rename Field | Fix a record field's name | — |
| Replace Derived Variable with Query | Compute, don't store | — |
| Change Reference to Value | Make it an immutable value | Change Value to Reference |
| Change Value to Reference | Share one instance | Change Reference to Value |

**Simplifying conditional logic**

| Technique | Essence | Pairs with |
|---|---|---|
| Decompose Conditional | Name the condition and its legs | — |
| Consolidate Conditional Expression | Merge checks with one result | — |
| Replace Nested Conditional with Guard Clauses | Early-return the unusual cases | — |
| Replace Conditional with Polymorphism | Case dispatch → subclasses | — |
| Introduce Special Case | One object answers the special value | — |
| Introduce Assertion | State the assumption in code | — |

**Refactoring APIs**

| Technique | Essence | Pairs with |
|---|---|---|
| Separate Query from Modifier | Reads without side effects | — |
| Parameterize Function | Merge near-twins via a parameter | — |
| Remove Flag Argument | Explicit function per flag value | — |
| Preserve Whole Object | Pass the object, not its parts | Replace Parameter with Query |
| Replace Parameter with Query | Let the callee work it out | Replace Query with Parameter |
| Replace Query with Parameter | Make callers pass it in | Replace Parameter with Query |
| Remove Setting Method | Fix the field at construction | — |
| Replace Constructor with Factory Function | Free construction from constructor limits | — |
| Replace Function with Command | Function → object with state | Replace Command with Function |
| Replace Command with Function | Flatten a needless command object | Replace Function with Command |

**Dealing with inheritance**

| Technique | Essence | Pairs with |
|---|---|---|
| Pull Up Method | Unify duplicate sibling methods | Push Down Method |
| Pull Up Field | Share a field in the superclass | Push Down Field |
| Pull Up Constructor Body | Common construction moves up | — |
| Push Down Method | Behavior only some subclasses need | Pull Up Method |
| Push Down Field | Data only some subclasses need | Pull Up Field |
| Replace Type Code with Subclasses | Type code → class per value | Remove Subclass |
| Remove Subclass | Subclass → field on the parent | Replace Type Code with Subclasses |
| Extract Superclass | Share the common part upward | Collapse Hierarchy |
| Collapse Hierarchy | Merge near-identical parent and child | Extract Superclass |
| Replace Subclass with Delegate | Inheritance axis → composition | Replace Superclass with Delegate |
| Replace Superclass with Delegate | Borrowed implementation → field | Replace Subclass with Delegate |

## Foundations

### Extract Function
Inverse: Inline Function.
Turn a fragment into a function named after its *purpose*, not its
mechanics. Use whenever you must read code to know what it does, or a
comment describes a block.
Steps: create the function and name it well (naming is the hard part — if
no good name comes, don't extract); copy the fragment in; pass locals it
reads as parameters and return the one it assigns for later use (more than
one assigned local — extract a smaller piece instead); replace the original
fragment with a call; hunt for duplicates of the fragment and replace them
too.

### Inline Function
Inverse: Extract Function.
Collapse a function whose body is as clear as its name, or unwind bad
indirection before re-extracting along better lines.
Steps: confirm it is not overridden anywhere; find every caller; replace
each call with the body one at a time; remove the definition. If a call
site is awkward, leave it for later — inline what is easy first.

### Extract Variable
Inverse: Inline Variable.
Name a subexpression to break a dense expression into readable, debuggable
parts.
Steps: confirm the expression has no side effects; introduce an immutable
variable set to it; replace each occurrence. If the name belongs to the
wider context, extract a function instead.

### Inline Variable
Inverse: Extract Variable.
Remove a variable whose name says no more than the expression itself, or
that blocks a neighboring refactoring.
Steps: confirm the assigned expression is side-effect-free; replace each
reference with the expression; delete the declaration.

### Change Function Declaration
Rename a function, or add/remove/reorder parameters — names and signatures
are the joints of the codebase.
Steps (simple, when all callers are reachable and few): edit the
declaration and every caller in one motion.
Steps (migration, for many or unreachable callers): extract the body into a
new function with the desired declaration; make the old one forward to it;
migrate callers one by one; delete the old function — or mark it deprecated
and keep it forwarding if the interface is published.

### Encapsulate Variable
Route access to widely-used mutable data through functions, creating a
monitoring and interception point before restructuring the data itself.
Steps: write getter/setter functions; replace each direct read/write with a
call; restrict the raw variable's visibility; for record values, consider
also returning copies so callers cannot mutate the original unseen.

### Rename Variable
Make a name say what the value is. Steps: for a name confined to a small
scope, just change declaration and uses; for a widely visible name, apply
Encapsulate Variable first, then rename inside the capsule.

### Introduce Parameter Object
Replace values that always travel together with one structure, shrinking
signatures and giving the concept a name that attracts behavior.
Steps: create the type (prefer a value object with equality); use Change
Function Declaration to add a parameter of the new type; have each caller
pass an instance; replace uses of the old parameters with reads from the
object, removing the old parameters one at a time.

### Combine Functions into Class
When several functions operate on the same data, bind them and the data
into a class. Steps: encapsulate the shared data (Encapsulate Record if it
is a bare record); create a class holding it; move each function in (Move
Function), dropping the now-implicit data parameters from its signature.

### Combine Functions into Transform
Alternative to the class form: one transform function takes the source data
and returns an enriched copy carrying all derived values.
Steps: create the transform taking the source and returning a deep copy;
move each derivation calculation into it, writing its result onto the copy;
change clients to read the enriched fields. Prefer the class form when the
source data is updated anywhere — a transform's copies go stale.

### Split Phase
When one block deals with two different concerns in sequence (parse then
compute, compute then format), split it into phases communicating through
an intermediate data structure.
Steps: extract the second phase as a function; introduce the intermediate
structure as its argument; move each value the second phase needs from its
parameters into the structure, one field at a time; extract the first phase
as a function returning the structure.

## Encapsulation

### Encapsulate Record
Replace a mutable bare record with a class so access is controlled and the
stored shape can evolve independently of its users.
Steps: encapsulate the variable holding the record; wrap the record in a
class exposing accessors; migrate readers/writers from raw fields to
accessors; for nested structures decide depth of protection — return copies
where callers must not mutate.

### Encapsulate Collection
A getter that hands out the underlying list lets callers mutate it behind
the owner's back.
Steps: add add/remove methods on the owning class; find and reroute every
direct mutation of the collection through them; make the getter return a
copy or read-only view.

### Replace Primitive with Object
Grow a domain type out of a bare number or string the moment the value
needs any behavior (validation, formatting, comparison).
Steps: encapsulate the variable; create a small value class wrapping the
primitive (constructor validates, getter returns it); adjust the setter and
getter to wrap/unwrap; then migrate behavior from callers onto the class
piece by piece.

### Replace Temp with Query
Turn a temp holding a computed value into a function, so extracted sibling
functions can share it and the computation has one home.
Steps: works best in a class, on a temp assigned once whose computation is
side-effect-free; extract the computation into a getter; inline the temp.

### Extract Class
Inverse: Inline Class.
Split a class doing two jobs. Steps: create the new class and link the old
one to it; move fields one at a time (Move Field); move methods (Move
Function), starting with the lowest-level; review interfaces, decide
whether clients see the new object or reach it through the old.

### Inline Class
Inverse: Extract Class.
Fold a class that no longer pulls its weight into its main user — also
useful as an intermediate: merge two badly-split classes, then re-extract
along better lines.
Steps: create forwarding methods on the absorbing class for the public
surface; redirect clients to the absorber; move features across until the
husk is empty; delete it.

### Hide Delegate
Inverse: Remove Middle Man.
Stop clients from navigating `server.delegate().feature()` — the extra hop
couples them to the object graph.
Steps: for each delegate feature clients use, add a forwarding method on
the server; redirect clients to it; if nothing external uses the delegate
accessor anymore, remove it.

### Remove Middle Man
Inverse: Hide Delegate.
When a class has become a wall of forwarders, let clients talk to the
delegate directly. Steps: add an accessor for the delegate; for each
forwarding method, redirect its clients to call through the accessor and
delete the forwarder. There is no absolute right amount of hiding — adjust
as the system shifts.

### Substitute Algorithm
Replace a convoluted implementation wholesale with a clearer one that does
the same job.
Steps: shrink the function first — this technique wants the smallest
possible replacement unit; write the new algorithm; run old and new against
the same suite of inputs until they agree everywhere; swap it in. This is
the coarsest technique here — the only one that replaces rather than
transforms — so it leans hardest on the tests.

## Moving features

### Move Function
Relocate a function to the module/class whose data and functions it
actually works with (see Feature Envy).
Steps: examine everything it uses in its current home — consider moving
companions first; check it is not overridden; copy it to the target and
adapt (context arrives via parameter or reference); turn the original into
a forwarder; then inline the forwarder away, or keep it if the old location
is a published interface.

### Move Field
Data structures must be right before behavior can be: move a field to the
record/class it really belongs with (where it changes together with its
neighbors).
Steps: encapsulate the source field; create the field plus accessors on the
target; rewire the source accessors to read/write the target (decide how
the source reaches the target — often an existing reference); remove the
source field.

### Move Statements into Function
Inverse: Move Statements to Callers.
When the same statements accompany every call to a function, they belong
inside it.
Steps: use Slide Statements to bring them adjacent to the call; with few
callers, cut and paste them in; otherwise extract a function containing the
statements plus the call, redirect all callers to it, then inline the old
function and rename.

### Move Statements to Callers
Inverse: Move Statements into Function.
When callers increasingly diverge on some part of a shared function's
behavior, push that part out to the boundary.
Steps: slide the divergent statements to the start or end of the function;
with few callers, cut and paste them out; otherwise Extract Function on
what stays, inline the original into each caller, remove it, and rename the
extracted remainder.

### Replace Inline Code with Function Call
On spotting code that duplicates what an existing function does, call the
function instead. Steps: replace and test; if the tests fail, the semantics
differed — revert. Library functions win over hand-rolled loops.

### Slide Statements
Move related statements next to each other — usually as preparation for an
extraction.
Steps: find the target position; check the slide is legal: the fragment
cannot cross anything that writes what it reads, reads what it writes, or
whose side-effect order matters; move it; on trouble, slide smaller pieces.

### Split Loop
A loop doing several jobs forces every reader to understand all of them.
Steps: copy the whole loop; delete one job's code from each copy so each
does a single job; then Extract Function on each loop. Do not fear the
extra iteration — split first for clarity, and re-merge only if a profiler
later says this loop matters.

### Replace Loop with Pipeline
Rewrite an accumulating loop as a chain of collection operations
(filter/map/reduce) where each stage names its purpose.
Steps: create a pipeline variable from the source collection; migrate one
piece of loop behavior at a time into a pipeline stage, deleting it from
the loop; remove the empty loop.

### Remove Dead Code
Unused code taxes every reader who stops to understand it.
Steps: confirm nothing references it (search; lean on the compiler); delete
it. Do not keep it "just in case" or comment it out — version control
remembers.

## Organizing data

### Split Variable
A variable assigned more than once (other than loop/accumulator roles) is
carrying more than one meaning.
Steps: at its first assignment, rename it for that first meaning and make
it immutable if the language allows; keep the new name up to the second
assignment; there, declare a fresh appropriately-named variable; repeat per
assignment.

### Rename Field
Names in record structures matter even more than local names — they spread.
Steps: for a narrowly scoped record, rename directly; otherwise Encapsulate
Record first, rename the private field, adjust accessors, then rename the
accessors with Change Function Declaration.

### Replace Derived Variable with Query
Never store what can be calculated: stored derivations are mutable data
that can go stale.
Steps: find every update to the derived variable; write a query computing
the value; use Introduce Assertion to check query equals variable at each
read; replace reads with the query; delete the variable and its updates.

### Change Reference to Value
Inverse: Change Value to Reference.
Make an inner object a value: immutable, replaced whole rather than
mutated, safely shareable and comparable.
Steps: check the candidate can be immutable (no one depends on observing
its mutations); change each modifier to produce/assign a new instance
instead of mutating; give the type value-based equality.

### Change Value to Reference
Inverse: Change Reference to Value.
When many copies of the same logical entity must stay consistent under
update, share one instance instead.
Steps: create a repository/registry for the instances; have constructors or
factories look the entity up rather than build a fresh copy; keep the
repository's scope as narrow as the sharing requires.

## Simplifying conditional logic

### Decompose Conditional
A long condition and long legs bury *why* in *how*.
Steps: Extract Function on the condition, naming what it tests; extract
each leg, naming what it does; once legs are single calls, a conditional
expression (ternary) often reads best.

### Consolidate Conditional Expression
Several separate checks that all produce the same result are one check in
disguise.
Steps: verify none of the conditions has side effects; merge two at a time
with and/or; finish with Extract Function so the combined condition gets a
name. Do not consolidate checks that are genuinely independent decisions.

### Replace Nested Conditional with Guard Clauses
When one path is the normal case and the rest are unusual exits, nesting
buries the normal path.
Steps: for each unusual case, in order, replace its nesting with an early
return (guard); flatten what remains into straight-line normal-path code;
inverting a condition often unlocks the next flattening. If both legs are
equally normal, keep a symmetric if/else instead.

### Replace Conditional with Polymorphism
When the same discriminator drives conditionals in several functions, give
each case its own class and let dispatch replace the conditions.
Steps: create the hierarchy (Replace Type Code with Subclasses) and a
factory returning the right subclass; copy one conditional-bearing function
into a subclass, reduce it to that case's leg; repeat per case; leave the
default leg in the superclass method, or make it abstract when every case
overrides. Reserve this for repeated or complex dispatch — a single simple
switch in one place does not need a class hierarchy.

### Introduce Special Case
The same "is it the special value?" check (null, missing, unknown) copied
across many call sites.
Steps: create a special-case object that answers the common questions with
the agreed defaults; return it from the data source instead of the raw
special value; delete the scattered checks, replacing them with plain
calls; keep an explicit probe for the few places that genuinely behave
differently. A literal/frozen record suffices when the special case only
answers reads.

### Introduce Assertion
Make an assumption the code silently relies on explicit and self-checking.
Steps: at the point the assumption must hold, add an assertion stating it.
Assertions target programmer errors only — never expected runtime
conditions — and the program must behave identically with them removed.

## Refactoring APIs

### Separate Query from Modifier
A function that returns a value should have no observable side effects;
callers can then call it anywhere, any number of times.
Steps: copy the function under a query name; strip all side effects from
the copy; strip the return value from the original (now the modifier);
update callers that used both aspects to call query then modifier.

### Parameterize Function
Several functions identical except for embedded literal values become one
function with a parameter.
Steps: pick one variant (preferably a middle case for ranges); use Change
Function Declaration to add the parameter; update its callers; replace the
literals in the body with the parameter; redirect the sibling functions'
callers one variant at a time; delete the siblings.

### Remove Flag Argument
A boolean/enum argument the caller sets to choose what the function does
hides the options and complicates the body.
Steps: create one explicitly named function per flag value (Decompose
Conditional helps carve them out); redirect every caller that passes a
literal flag to the matching explicit function; retire the flagged function
or leave it as an internal dispatcher when the flag value arrives as
genuine data.

### Preserve Whole Object
Counterpart tension: Replace Parameter with Query.
Callers that unpack an object's fields just to pass them along should pass
the object.
Steps: declare the desired signature as a new (or empty wrapper) function;
fill its body by pulling values from the object, calling the old logic;
redirect callers to it; inline the old function; skip this when the callee
should *not* know about the object — a dependency is a real cost.

### Replace Parameter with Query
Inverse: Replace Query with Parameter.
Drop a parameter the callee can determine for itself (often derivable from
another parameter); shorter signatures shift responsibility to the callee.
Steps: confirm the determination adds no unwanted dependency and the
function stays side-effect-free (referentially transparent); extract the
argument computation if needed; replace body uses of the parameter with the
query; remove the parameter via Change Function Declaration.

### Replace Query with Parameter
Inverse: Replace Parameter with Query.
Purge an internal reference to something unpleasant — a global, mutable
shared state — by making callers pass the value in.
Steps: Extract Variable on the query result inside the body; extract the
body-minus-query as a new function taking it as a parameter; inline
outward until callers supply the value. Cost: callers must now figure out
the argument; use when making the callee pure is worth that.

### Remove Setting Method
A setter advertises that a field may change; remove it when the field
should be fixed at construction.
Steps: add the value to the constructor (Change Function Declaration) if
not already there; migrate each creation-then-set call site to construct
with the value; delete the setter.

### Replace Constructor with Factory Function
Constructors are constrained (fixed name, must return a new instance of
that class); a factory function is not.
Steps: create a factory that calls the constructor; replace each
construction call with the factory; restrict the constructor's visibility
as far as the language allows.

### Replace Function with Command
Inverse: Replace Command with Function.
Reify a function into an object whose execution is its purpose — gaining
fields for its state, decomposition room for a huge tangled body, or
lifecycle control.
Steps: create a class named for the function; move the function in as its
`execute`; promote parameters and stubborn temps to fields set in the
constructor; then continue extracting inside the class, where all state is
reachable without parameter plumbing. Prefer a plain function whenever one
suffices — commands are deliberate extra machinery.

### Replace Command with Function
Inverse: Replace Function with Command.
When a command object's only job is running its body, flatten it back.
Steps: extract a plain function wrapping construct-plus-execute; inline the
command's internals into it (fields become locals/parameters); delete the
class.

## Dealing with inheritance

### Pull Up Method
Inverse: Push Down Method.
Duplicate methods in sibling subclasses drift apart silently; unify them in
the superclass.
Steps: verify the bodies are identical — if only similar, refactor them
into identical shape first (Parameterize Function for value differences;
pull up the fields/methods they depend on beforehand); copy to the
superclass; delete from each subclass one at a time.

### Pull Up Field
Inverse: Push Down Field.
Steps: confirm the sibling fields are used equivalently; rename to a common
name if needed; create the field in the superclass with visibility the
subclasses can use; delete the subclass fields.

### Pull Up Constructor Body
Common statements at the start of sibling constructors belong in the
superclass constructor.
Steps: define/identify the superclass constructor; move the common
statements into it, invoked via the subclass's superclass-constructor call;
if common code follows subclass-specific code, Extract Function on it first
and pull up the call.

### Push Down Method
Inverse: Pull Up Method.
Behavior relevant to only some subclasses should live there — but only when
callers know which subclass they hold; otherwise replace the conditional
dispatch with polymorphism instead.
Steps: copy the method into each subclass that needs it; remove it from the
superclass.

### Push Down Field
Inverse: Pull Up Field.
Steps: declare the field in each subclass that uses it; remove it from the
superclass.

### Replace Type Code with Subclasses
Inverse: Remove Subclass.
Give values of a type-code field their own classes, so type-specific
behavior can attach polymorphically.
Steps: self-encapsulate the type code behind a getter; pick one value,
create its subclass overriding the getter to return the constant; route
construction through a factory that selects the subclass; repeat per value;
remove the raw field once all getters are overrides; then migrate
type-dependent behavior in (Push Down Method, Replace Conditional with
Polymorphism). When the host class is already subclassed for something
else — or instances change type at runtime — subclass the type-code
*property object* instead of the host.

### Remove Subclass
Inverse: Replace Type Code with Subclasses.
A subclass too small to justify its existence costs more than a field.
Steps: replace direct constructions of the subclass with a superclass
factory; replace type checks on the subclass with checks on a new
representative field; empty the subclass (Push Up anything shared); delete
it.

### Extract Superclass
Related: Collapse Hierarchy undoes a pointless one.
Two classes doing similar work can share a parent that owns the common
part. Duplication removal is the motive — inheritance here is mechanics,
not taxonomy.
Steps: create an empty superclass and make both classes extend it; pull up
common fields, methods, and constructor body one element at a time; examine
clients — some may now depend on the superclass interface instead.

### Collapse Hierarchy
When a class and its parent have grown so alike the boundary adds nothing,
merge them.
Steps: choose the survivor (keep the better name); move everything into it
with Pull Up / Push Down; repoint references to the removed class; delete
it.

### Replace Subclass with Delegate
See also Replace Superclass with Delegate.
Inheritance grants one axis of variation and welds it in at construction;
delegation frees the axis when it is needed for something else, must change
at runtime, or couples child to parent too tightly.
Steps: create a delegate class capturing the subclass's variant behavior;
add a superclass field referencing it, filled by the factory/constructor
for the relevant cases; move each subclass override into the delegate,
making the superclass method forward to the delegate when present and keep
its default otherwise; when the subclass is empty, delete it and replace
its construction with delegate attachment. Inheritance is still the simpler
tool where it fits — delegate when it strains, not by default.

### Replace Superclass with Delegate
When a class inherits mostly to borrow implementation, and parts of the
superclass make no sense on it, inheritance is the wrong claim
(the classic case: a domain type extending a collection class).
Steps: add a field in the subclass holding an instance of the superclass;
add forwarding methods for each inherited feature genuinely used; sever the
extends relationship. The result exposes only operations that make sense on
the type, at the cost of writing the forwarders.
