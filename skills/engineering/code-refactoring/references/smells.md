# Code Smells — Diagnosis Reference

A smell is a structure that suggests — not proves — a refactoring
opportunity. Use this file symptom-first: match what you see in the code to
a row of the index below and take its techniques (step sequences live under
matching `###` headings in `techniques.md`); open a smell's own `## <Name>`
entry only when the index row leaves the match or the remedy unclear. No
metric replaces judgment; these are cues, not rules.

## Index

| Smell | Telltale sign | Apply |
|---|---|---|
| Mysterious Name | Name doesn't say what it's for | Change Function Declaration, Rename Variable, Rename Field |
| Duplicated Code | Same structure in more than one place | Extract Function, Slide Statements, Pull Up Method |
| Long Function | Must read line by line to understand | Extract Function, Replace Temp with Query, Decompose Conditional |
| Long Parameter List | Call sites hard to write and read | Introduce Parameter Object, Preserve Whole Object, Remove Flag Argument |
| Global Data | Writable from anywhere, changes untraceable | Encapsulate Variable |
| Mutable Data | An update here breaks an assumption there | Encapsulate Variable, Split Variable, Separate Query from Modifier |
| Divergent Change | One module changes for unrelated reasons | Split Phase, Move Function, Extract Class |
| Shotgun Surgery | One change forces edits in many modules | Move Function, Move Field, Combine Functions into Class |
| Feature Envy | Function lives off another module's data | Move Function, Extract Function |
| Data Clumps | Same three or four items always travel together | Extract Class, Introduce Parameter Object |
| Primitive Obsession | Domain concepts as bare numbers or strings | Replace Primitive with Object, Replace Type Code with Subclasses |
| Repeated Switches | Same switch logic in several places | Replace Conditional with Polymorphism |
| Loops | Loop obscures what is being computed | Replace Loop with Pipeline |
| Lazy Element | Structure that no longer earns its keep | Inline Function, Inline Class, Collapse Hierarchy |
| Speculative Generality | Machinery for a future that never came | Collapse Hierarchy, Inline Function, Remove Dead Code |
| Temporary Field | Field valid only in certain situations | Extract Class, Introduce Special Case |
| Message Chains | Clients navigate `a.b().c().d()` | Hide Delegate, Extract Function, Move Function |
| Middle Man | Interface mostly forwards elsewhere | Remove Middle Man, Inline Function |
| Insider Trading | Modules trade private data off the books | Move Function, Move Field, Hide Delegate |
| Large Class | Too many fields and responsibilities | Extract Class, Extract Superclass |
| Alternative Classes with Different Interfaces | Would-be substitutes with mismatched signatures | Change Function Declaration, Move Function |
| Data Class | Getters and setters and nothing else | Encapsulate Record, Move Function, Remove Setting Method |
| Refused Bequest | Subclass uses a fraction of its inheritance | Push Down Method, Replace Subclass with Delegate |
| Comments (as deodorant) | Thick comment masking bad code | Extract Function, Change Function Declaration, Introduce Assertion |

## Mysterious Name

A function, variable, class, or field whose name does not say what it is
for; readers must open the implementation to find out.
**Apply:** Change Function Declaration (rename functions), Rename Variable,
Rename Field.
If no good name will come, that is usually a deeper design problem —
untangle the element first and the name follows.

## Duplicated Code

The same or near-same structure in more than one place, so every change must
be found and repeated everywhere.
**Apply:** Extract Function to unify identical fragments; Slide Statements
first when fragments are merely similar, to line up the common part for
extraction; Pull Up Method when the duplication sits in sibling subclasses.

## Long Function

A function you must read line by line to understand. Length itself is not
the trigger — the trigger is distance between what it does and how; a
one-line block worth a comment is worth a function named for its purpose.
**Apply:** Extract Function (covers nearly every case). When parameters and
temps block extraction: Replace Temp with Query, Introduce Parameter Object,
Preserve Whole Object; as a last resort Replace Function with Command.
Extraction signals: a comment (extract what it describes and name it after
the purpose), a conditional (Decompose Conditional; for switches, extract
each leg; for repeated same-condition switches, Replace Conditional with
Polymorphism), a loop (extract loop plus body; if the extraction is hard to
name, Split Loop — it is doing several jobs).

## Long Parameter List

So many parameters that call sites are hard to write and read.
**Apply:** Replace Parameter with Query (when one parameter is derivable
from another), Preserve Whole Object (when several fields of one structure
are passed separately), Introduce Parameter Object (for values that travel
together), Remove Flag Argument (for booleans selecting behavior), Combine
Functions into Class (when several functions share the same parameters).

## Global Data

Values writable from anywhere, with no way to see who changed them —
global variables, class-level statics, singletons alike.
**Apply:** Encapsulate Variable — route access through a function, then
narrow its scope into a module or class. Mutable global state is the worst
form; even small amounts deserve encapsulation.

## Mutable Data

A value updated in one place breaks an assumption held elsewhere; the more
widely the data is visible, the greater the risk.
**Apply:** Encapsulate Variable (funnel updates through few functions),
Split Variable (one variable reused for different meanings), Slide
Statements + Extract Function (separate side-effect-free logic from the
mutation), Separate Query from Modifier, Remove Setting Method, Replace
Derived Variable with Query (never store what can be computed), Combine
Functions into Class / into Transform (shrink the code that may update),
Change Reference to Value (replace whole values instead of mutating parts).

## Divergent Change

One module keeps changing for unrelated reasons — different kinds of
requirement each touch a different subset of it. The module mixes contexts.
**Apply:** Split Phase when the contexts run in sequence (pass a data
structure between them); otherwise Move Function to separate the contexts
into their own modules, with Extract Function first when single functions
mix both, or Extract Class when the module is a class.

## Shotgun Surgery

The mirror image: one kind of change forces small edits in many modules,
and one missed edit means a bug.
**Apply:** Move Function and Move Field to gather the scattered logic into
one place; Combine Functions into Class when the pieces operate on shared
data; Combine Functions into Transform when they enrich a structure; Split
Phase when they form a sequence. Inlining (Inline Function, Inline Class)
is legitimate here: pull the fragments together first, even into something
temporarily too big, then re-split along better lines.

## Feature Envy

A function that communicates more with another module's data than with its
own — typically calling half a dozen getters on one foreign object.
**Apply:** Move Function to put it with the data it envies; Extract
Function first when only part of the function envies. When it uses several
modules, move it toward the one supplying most of its data.

## Data Clumps

The same three or four data items traveling together through fields and
parameter lists. Test: delete one of them — do the others still mean
anything? If not, they belong in an object.
**Apply:** Extract Class on the fields (a real class, not a bare record —
it becomes a home for behavior later), then Introduce Parameter Object or
Preserve Whole Object to shrink the signatures.

## Primitive Obsession

Domain concepts — money, coordinates, ranges, phone numbers — represented
as bare numbers and strings, with validation and formatting logic smeared
across callers.
**Apply:** Replace Primitive with Object; Replace Type Code with Subclasses
plus Replace Conditional with Polymorphism when the primitive is a type
code steering conditionals; Extract Class / Introduce Parameter Object when
the primitives clump.

## Repeated Switches

The same switch/if-else chain over the same discriminator in several
places, so adding one case means hunting down every copy.
**Apply:** Replace Conditional with Polymorphism. A single switch in one
place is fine; repetition is what condemns it.

## Loops

An explicit loop that obscures what is being selected or computed.
**Apply:** Replace Loop with Pipeline (filter/map/reduce style) where the
language supports first-class functions; each pipeline stage states its
purpose.

## Lazy Element

A structure that no longer earns its keep — a function whose body says
exactly what its name says, a class that is one method in disguise.
**Apply:** Inline Function, Inline Class; Collapse Hierarchy when the
element is a nearly-empty layer in an inheritance chain.

## Speculative Generality

Hooks, parameters, and abstract layers added for a future that never
arrived. If all the machinery were used, it would be fine; unused, it only
obstructs.
**Apply:** Collapse Hierarchy (pointless abstract layers), Inline Function /
Inline Class (needless indirection), Change Function Declaration (drop
unused parameters), Remove Dead Code. An element used only by tests is this
smell: delete those tests, then Remove Dead Code.

## Temporary Field

A field set only in certain situations and null otherwise, forcing readers
to reason about when it is valid.
**Apply:** Extract Class to give the occasional data its own home, Move
Function to bring the related code with it, Introduce Special Case to
replace the "not valid now" state with an explicit object.

## Message Chains

Client code navigating `a.b().c().d()` — coupled to every link; any change
along the path breaks the caller.
**Apply:** Hide Delegate at some link in the chain; often better, find what
the final object is used for, Extract Function on that usage, and Move
Function to push it down the chain toward the data.

## Middle Man

A class whose interface mostly forwards to another object; the delegation
has stopped adding value.
**Apply:** Remove Middle Man (let clients talk to the real object), Inline
Function for a handful of trivial forwarders, Replace Subclass/Superclass
with Delegate when the middle man has real behavior of its own.

## Insider Trading

Modules that trade private data back and forth off the books — deep mutual
knowledge and coupling. Subclasses prying into superclass internals are the
classic case.
**Apply:** Move Function and Move Field to relocate the traded data and
logic; Hide Delegate to make a third party mediate; Replace Subclass with
Delegate or Replace Superclass with Delegate when inheritance is the
conduit.

## Large Class

Too many fields, too many responsibilities, and usually duplication among
its methods.
**Apply:** Extract Class, grouping fields that change together (shared name
prefixes/suffixes are a hint); Extract Superclass or Replace Type Code with
Subclasses when subsets suggest a hierarchy. Look at how clients use the
class — each distinct subset of its surface is a candidate split.

## Alternative Classes with Different Interfaces

Two classes that could substitute for each other, except their method
signatures do not line up.
**Apply:** Change Function Declaration to align signatures, Move Function
until the protocols match, Extract Superclass if duplication emerges.

## Data Class

Fields with getters and setters and nothing else; the behavior that
belongs to the data lives in its clients.
**Apply:** Encapsulate Record on public fields, Remove Setting Method on
fields that should not change, then find where clients manipulate the data
and Move Function (with Extract Function as needed) to bring that behavior
home. Exception: immutable result records passed between processing phases
are fine as plain data.

## Refused Bequest

A subclass that uses only a fraction of what it inherits. Mild when it
merely ignores inherited implementation — often not worth fixing. Strong
when it refuses the *interface*.
**Apply:** For the mild form, create a sibling and Push Down Method / Push
Down Field so the superclass holds only what is shared. For refused
interfaces, leave the hierarchy: Replace Subclass with Delegate or Replace
Superclass with Delegate.

## Comments (as deodorant)

Comments are not a smell — but a thick comment explaining bad code is
masking one. Refactor until the comment is redundant.
**Apply:** Extract Function on the block the comment describes, Change
Function Declaration to make the name carry the explanation, Introduce
Assertion when the comment states a precondition. Comments that remain
valuable: why something is done, and notes on genuine uncertainty.
