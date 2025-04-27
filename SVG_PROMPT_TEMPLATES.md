# SVG Generation Prompt Templates

This document provides a collection of prompt templates optimized for generating SVG diagrams using Claude. These templates are specifically designed for the GenAI Agent 3D system to produce SVGs that convert well to 3D.

## Guidelines for Effective SVG Generation

When creating prompts for SVG generation, consider the following principles:

1. **Be specific about structural elements**: Clearly define the components and their relationships
2. **Specify visual attributes**: Include sizing, colors, and styling information
3. **Establish naming conventions**: Request IDs and classes for elements to aid in processing
4. **Request clear labels**: Ask for readable, well-positioned text
5. **Define hierarchy**: Clarify which elements should be grouped together
6. **Specify connector types**: Indicate how elements should be connected
7. **Include directional information**: Specify flow direction where applicable

## General SVG Diagram Template

```
Generate an SVG diagram showing [subject matter]. The diagram should:

1. Use a [width] x [height] viewBox with a white background
2. Include the following elements:
   - [Element 1] represented as [shape] in [color]
   - [Element 2] represented as [shape] in [color]
   - [Element 3] represented as [shape] in [color]
3. Connect the elements with [connector style] according to this relationship: [describe relationships]
4. Label each element with readable text in [font size]pt [font family]
5. Include a title at the top: "[diagram title]"
6. Use meaningful IDs for elements following this pattern: [ID pattern]
7. Group related elements together with appropriate group elements
8. Use a consistent color scheme including [color list]

Please provide a clean, valid SVG that can be easily converted to 3D with clear separation between elements.
```

## Technical Architecture Diagram Template

```
Create an SVG diagram of a [type] architecture with the following components:

1. Use a 1000 x 800 viewBox with 20px padding inside
2. Include these components:
   - [Component 1]: Rectangle with rounded corners (10px radius), [color] fill, positioned in the [position]
   - [Component 2]: Rectangle with rounded corners (10px radius), [color] fill, positioned in the [position]
   - [Component 3]: Rectangle with rounded corners (10px radius), [color] fill, positioned in the [position]
3. Connect components with directional arrows showing data/process flow:
   - [Component 1] to [Component 2]: [describe relationship]
   - [Component 2] to [Component 3]: [describe relationship]
4. Label each component with its name centered inside the shape
5. Add small icons or symbols inside each component representing their function
6. Group components by [grouping criteria] using <g> elements with appropriate IDs
7. Use this color scheme: [primary color], [secondary color], [accent color]
8. Add a legend explaining symbols and color meanings
9. Use consistent stroke widths: 2px for containers, 1.5px for connectors

Ensure all elements have unique IDs following the pattern: [component-type]-[number]
```

## Network Topology Diagram Template

```
Generate an SVG diagram of a network topology with the following specifications:

1. Use a 1200 x 900 viewBox with a light grid background (optional)
2. Include these network components:
   - [Network Device 1]: Use a [device icon style] at position [x,y]
   - [Network Device 2]: Use a [device icon style] at position [x,y]
   - [Network Device 3]: Use a [device icon style] at position [x,y]
3. Connect devices with appropriate line styles:
   - [Connection 1]: [line style] with [protocol label]
   - [Connection 2]: [line style] with [protocol label]
4. Create network segments/zones using lightly colored background shapes
5. Add a title: "[Network Name] Topology"
6. Label each device with name and IP information
7. Include a legend for connection types
8. Use networking standard colors: [ethernet color], [fiber color], [wireless color]
9. Group devices by network zones: [zone 1], [zone 2]

Add protocol indicator icons at midpoints of connections. Ensure each network device has a unique ID like "device-[type]-[number]" and each connection has an ID like "conn-[source]-[target]".
```

## Software Class Diagram Template

```
Create an SVG class diagram following UML standards for the following classes:

1. Use a 1200 x 1000 viewBox with white background
2. Define these classes:
   - [Class 1]: Rectangle with three sections (name, attributes, methods)
     - Attributes: [list attributes with types]
     - Methods: [list methods with parameters and return types]
   - [Class 2]: Rectangle with three sections
     - Attributes: [list attributes with types]
     - Methods: [list methods with parameters and return types]
3. Show these relationships:
   - [Class 1] [relationship type] [Class 2] with proper UML notation
   - [Class 3] [relationship type] [Class 4] with proper UML notation
4. Use standard UML notation for relationship lines:
   - Inheritance: Empty triangle arrow
   - Association: Simple line
   - Aggregation: Empty diamond
   - Composition: Filled diamond
5. Label relationships with multiplicity where appropriate
6. Use monospace font for class member details
7. Include proper visibility markers (+, -, #, ~)
8. Group related classes together

Use consistent spacing and alignment. Give each class an ID of "class-[name]" and each relationship an ID of "rel-[source]-[target]".
```

## Process Flow Diagram Template

```
Generate an SVG process flow diagram for [process name] with these specifications:

1. Use a 1000 x 600 viewBox with white background
2. Create a left-to-right flow direction
3. Include these process steps:
   - [Step 1]: Rounded rectangle with [color] fill
   - [Step 2]: Rounded rectangle with [color] fill
   - [Step 3]: Rounded rectangle with [color] fill
4. Include these decision points:
   - [Decision 1]: Diamond shape with yes/no paths
   - [Decision 2]: Diamond shape with yes/no paths
5. Connect steps with arrows showing process flow
6. Add annotations for important conditions or notes
7. Include start and end terminals as ovals
8. Use a consistent color scheme:
   - Process steps: [color]
   - Decisions: [color]
   - Start/End: [color]
9. Number each step in the process for easy reference

Make sure each element has a meaningful ID (e.g., "step-1", "decision-1"). Position elements with enough spacing to avoid cluttering. Use consistent font sizes for different element types.
```

## Data Flow Diagram Template

```
Create an SVG data flow diagram for [system name] with the following specifications:

1. Use a 1200 x 900 viewBox
2. Include these external entities as rectangles:
   - [Entity 1]: Rectangle in [color]
   - [Entity 2]: Rectangle in [color]
3. Include these processes as circles or rounded rectangles:
   - [Process 1]: Circle in [color]
   - [Process 2]: Circle in [color]
4. Include these data stores as open-ended rectangles:
   - [Data Store 1]: Open-ended rectangle in [color]
   - [Data Store 2]: Open-ended rectangle in [color]
5. Show data flows with labeled arrows:
   - [Flow 1]: From [source] to [destination] carrying [data description]
   - [Flow 2]: From [source] to [destination] carrying [data description]
6. Use distinct colors for different element types
7. Label each element clearly with a title
8. Group related elements together
9. Include data flow direction indicators on arrows

Make sure each element has a unique ID (e.g., "entity-customer", "process-validate", "store-orders"). Use dashed lines for internal boundaries if showing different system contexts.
```

## Hierarchy Diagram Template

```
Generate an SVG hierarchy diagram for [organization/system] with these specifications:

1. Use a 1000 x 1200 viewBox with white background
2. Create a top-down tree structure with:
   - [Top Level Element]: Rectangle at the top, [color] fill
   - [Second Level Elements]: Rectangles below, connected to parent, [color] fill
   - [Third Level Elements]: Rectangles below, connected to respective parents, [color] fill
3. Connect elements with vertical and horizontal lines showing reporting/dependency structure
4. Include labels for all elements, positioned inside each rectangle
5. Size elements based on their hierarchical importance
6. Create logical groupings with consistent colors
7. Add a title at the top: "[Organization/System] Hierarchy"
8. Use consistent spacing between hierarchy levels
9. Include a legend if using color-coding for different departments/types

Use a consistent font for element labels. Give each node an ID that reflects its position in the hierarchy (e.g., "level1-ceo", "level2-vp-sales").
```

## Cloud Architecture Diagram Template

```
Create an SVG diagram of a cloud architecture with these specifications:

1. Use a 1200 x 900 viewBox with a light blue (#f0f8ff) background
2. Include these cloud components:
   - [Cloud Service 1]: Use standard cloud service icon or rectangle with [service name] in [region/zone]
   - [Cloud Service 2]: Use standard cloud service icon or rectangle with [service name] in [region/zone]
   - [Cloud Service 3]: Use standard cloud service icon or rectangle with [service name] in [region/zone]
3. Group services by:
   - Virtual networks/VPCs as large rounded rectangles with light fill
   - Availability zones as dashed-line sections
   - Service categories as grouped elements
4. Connect services with appropriate flow lines:
   - Network connections as solid lines
   - Data flows as dashed arrows
   - Dependencies as dotted lines
5. Add security boundaries with appropriate iconography
6. Include a legend for all symbols and connection types
7. Label each service with its name and purpose
8. Use cloud-specific color coding:
   - Compute: [color]
   - Storage: [color]
   - Networking: [color]
   - Databases: [color]
   - Security: [color]

Ensure all elements have meaningful IDs (e.g., "service-ec2-webserver", "vpc-production"). Include service-specific icons inside each element when possible.
```

## State Diagram Template

```
Generate an SVG state diagram for [system/process] with these specifications:

1. Use a 1000 x 800 viewBox with white background
2. Include these states as rounded rectangles:
   - [State 1]: Rounded rectangle with [color] fill
   - [State 2]: Rounded rectangle with [color] fill
   - [State 3]: Rounded rectangle with [color] fill
3. Show transitions between states as arrows with:
   - Labels describing the event triggering the transition
   - Guards in square brackets [guard condition] when applicable
   - Actions after a forward slash /action
4. Include an initial state (filled circle) and final state(s) (circle with dot inside)
5. Add a title: "[System/Process] State Diagram"
6. Use consistent state sizing and spacing
7. Group related states visually
8. Include any nested states as smaller rounded rectangles inside parent states
9. Use consistent font styling for state names and transition labels

Ensure each state has an ID like "state-[name]" and each transition has an ID like "trans-[source]-[target]". Position transition labels to avoid overlapping with arrows or states.
```

## Entity Relationship Diagram Template

```
Create an SVG entity-relationship diagram for [database/system] with these specifications:

1. Use a 1200 x 800 viewBox with white background
2. Include these entities as rectangles:
   - [Entity 1]: Rectangle with entity name as header, attributes listed below
   - [Entity 2]: Rectangle with entity name as header, attributes listed below
   - [Entity 3]: Rectangle with entity name as header, attributes listed below
3. For each entity attribute:
   - Primary keys underlined or marked with PK
   - Foreign keys marked with FK
   - Required/optional status indicated
   - Data type included
4. Show relationships between entities with connecting lines:
   - One-to-many: Crow's foot notation
   - Many-to-many: Crow's foot on both ends
   - One-to-one: Single line with indicators
5. Label each relationship with a verb phrase
6. Include cardinality constraints at each end of relationships
7. Use consistent entity sizing and attribute formatting
8. Group related entities together
9. Use a muted color scheme with distinct colors for different entity types

Give each entity an ID like "entity-[name]" and each relationship an ID like "rel-[entity1]-[entity2]".
```

## Sequence Diagram Template

```
Generate an SVG sequence diagram for [interaction/process] with these specifications:

1. Use a 1400 x 900 viewBox with white background
2. Include these actors/objects across the top:
   - [Actor/Object 1]: Rectangle or stick figure labeled with name
   - [Actor/Object 2]: Rectangle or stick figure labeled with name
   - [Actor/Object 3]: Rectangle or stick figure labeled with name
3. Show vertical lifelines extending downward from each actor/object (dashed lines)
4. Include activation bars on lifelines when the object is active (thin rectangles)
5. Show messages between lifelines as horizontal arrows:
   - Synchronous calls: Solid arrow with filled head
   - Asynchronous calls: Solid arrow with open head
   - Responses: Dashed arrow with open head
6. Label each message with its name/description
7. Include time-ordered sequence from top to bottom
8. Show any loops, alt blocks, or opt blocks with labeled frames
9. Create any necessary self-calls as arrows that loop back
10. Include a title at the top: "[Interaction/Process] Sequence"

Make sure each actor/object has an ID like "actor-[name]" and each message has an ID like "msg-[number]". Add clear timing indicators or sequence numbers if necessary.
```

## Component Diagram Template

```
Create an SVG component diagram for [software system] with these specifications:

1. Use a 1200 x 900 viewBox with white background
2. Include these components as rectangles with the component stereotype icon:
   - [Component 1]: Rectangle with component name, in [color]
   - [Component 2]: Rectangle with component name, in [color]
   - [Component 3]: Rectangle with component name, in [color]
3. Show interfaces as:
   - Provided interfaces: Ball notation (circle on a line) or interface stereotype
   - Required interfaces: Socket notation (semicircle on a line) or interface stereotype
4. Connect components with appropriate dependency relationships
5. Group related components into packages or subsystems
6. Add a title: "[System Name] Component Diagram"
7. Include stereotypes for specialized components (e.g., «service», «database»)
8. Use consistent component sizing and interface placement
9. Add brief descriptions of key components' responsibilities

Ensure each component has an ID like "comp-[name]", each interface has an ID like "intf-[name]", and each relationship has an ID like "rel-[source]-[target]".
```

## Conceptual Model Diagram Template

```
Generate an SVG conceptual model diagram for [domain/concept] with these specifications:

1. Use a 1200 x 800 viewBox with white background
2. Include these concepts as boxes or rounded rectangles:
   - [Concept 1]: Rectangle with [color] fill, labeled clearly
   - [Concept 2]: Rectangle with [color] fill, labeled clearly
   - [Concept 3]: Rectangle with [color] fill, labeled clearly
3. Show relationships between concepts with connecting lines and appropriate labels
4. Use different line styles for different relationship types:
   - Is-a relationships: Solid line with arrow
   - Has-a relationships: Solid line with diamond
   - Uses relationships: Dashed line with arrow
5. Size concepts according to their importance or scope
6. Group related concepts together with light background colors
7. Add a title: "[Domain/Concept] Conceptual Model"
8. Include brief descriptions for complex concepts
9. Use a consistent, readable font throughout

Give each concept an ID like "concept-[name]" and each relationship an ID like "rel-[concept1]-[concept2]". Position relationship labels to avoid overlapping with lines or concepts.
```

## Example: AWS Architecture Diagram

Here's a filled example for the Cloud Architecture template:

```
Create an SVG diagram of an AWS architecture with these specifications:

1. Use a 1200 x 900 viewBox with a light blue (#f0f8ff) background
2. Include these cloud components:
   - VPC: Large rounded rectangle encompassing most components, light gray fill (#f5f5f5)
   - Public subnet: Rectangle with light green fill (#e6ffe6) in the top portion of the VPC
   - Private subnet: Rectangle with light yellow fill (#ffffeb) in the bottom portion of the VPC
   - Internet Gateway: Standard AWS IGW icon at the top edge of the VPC
   - Application Load Balancer: ALB icon in the public subnet
   - EC2 instances: Three EC2 icons in the private subnet
   - RDS database: RDS icon below the EC2 instances in the private subnet
   - S3 bucket: S3 icon outside the VPC on the right side
   - CloudFront: CloudFront icon at the top, above the VPC
3. Connect components with appropriate flow lines:
   - Internet to CloudFront: Arrow showing user requests
   - CloudFront to ALB: Arrow showing forwarded requests
   - ALB to EC2 instances: Arrows showing load balancing
   - EC2 to RDS: Arrow showing database queries
   - EC2 to S3: Dashed arrow showing object storage access
4. Group services by:
   - VPC boundary clearly marked
   - Subnet boundaries clearly differentiated
   - Security groups as dotted outlines around EC2 and RDS
5. Add security boundaries with lock icons where appropriate
6. Include a legend for all symbols and connection types
7. Label each service with its name and purpose
8. Use AWS-specific color coding:
   - Compute (EC2): Orange (#FF9900)
   - Storage (S3): Red (#CC2424)
   - Networking: Blue (#147EBA)
   - Databases: Blue (#3B48CC)
   - Security: Gray (#686868)

Ensure all elements have meaningful IDs (e.g., "service-alb-web", "vpc-production"). Include the standard AWS service icons inside each element.
```

## Example: Network Protocol Diagram

Here's a filled example for the General SVG Diagram template:

```
Generate an SVG diagram showing the TCP/IP protocol stack. The diagram should:

1. Use a 800 x 600 viewBox with a white background
2. Include the following elements:
   - Application Layer represented as a rectangle in light blue (#add8e6)
   - Transport Layer represented as a rectangle in light green (#90ee90)
   - Internet Layer represented as a rectangle in light yellow (#ffffe0)
   - Network Interface Layer represented as a rectangle in light orange (#ffd580)
3. Connect the elements with vertical arrows showing data flow both upward and downward through the stack
4. Label each element with readable text in 14pt Arial
   - Application Layer should list "HTTP, FTP, SMTP, DNS"
   - Transport Layer should list "TCP, UDP"
   - Internet Layer should list "IP, ICMP, ARP"
   - Network Interface Layer should list "Ethernet, Wi-Fi, PPP"
5. Include a title at the top: "TCP/IP Protocol Stack"
6. Use meaningful IDs for elements following this pattern: "layer-[name]"
7. Include right-side annotations showing encapsulation details at each layer (headers added)
8. Show a sample data packet transformation as it moves down the stack with growing headers

Please provide a clean, valid SVG that can be easily converted to 3D with clear separation between protocol layers and clear directional flow.
```

## Best Practices for SVG Optimization

To ensure SVGs convert well to 3D, follow these additional guidelines:

1. **Use simple, clean paths**: Avoid overly complex paths that would be difficult to extrude
2. **Keep elements separate**: Don't merge paths that represent different logical elements
3. **Maintain consistent scale**: Use similar proportions for related elements
4. **Use standard shapes when possible**: Prefer basic shapes (rect, circle) over custom paths when appropriate
5. **Apply meaningful grouping**: Group elements that should move together in 3D
6. **Clear spacing between elements**: Maintain adequate space for proper 3D separation
7. **Consistent stroke widths**: Use standardized stroke widths throughout the diagram
8. **Avoid overlapping elements**: Separate elements that should be distinct in 3D
9. **Use flat colors**: Avoid gradients that may be difficult to represent in 3D materials
10. **Add depth hints**: Consider adding comments or special attributes to suggest relative 3D depth

By following these templates and guidelines, you can generate SVG diagrams that are optimized for conversion to 3D visualizations in the GenAI Agent 3D system.
