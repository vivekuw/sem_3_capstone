# Plant Knowledge Graph (KG) Schema Specification

This document details the ontology and graph schema for the Tennessee Eastman Process (TEP) Root Cause Analysis Knowledge Graph hosted in Neo4j.

---

## 1. Node Labels

### `:Unit`
Represents physical process unit operations in the chemical flowsheet.
* **`id`** (`String`, Unique): E.g., `UNIT_REACTOR`, `UNIT_CONDENSER`, `UNIT_SEPARATOR`, `UNIT_COMPRESSOR`, `UNIT_STRIPPER`, `UNIT_FEED`, `UNIT_PRODUCT`.
* **`name`** (`String`): Descriptive name, e.g., `"Chemical Reactor"`.
* **`description`** (`String`): Functional role in the process flowsheet.

### `:Sensor`
Represents physical instrumentation transmitting continuous time-series process measurements (XMEAS 1-41 and XMVs).
* **`id`** (`String`, Unique): E.g., `XMEAS_9`.
* **`tag`** (`String`, Indexed): Instrumentation tag, e.g., `REACTOR_TEMP`.
* **`variable_name`** (`String`): Physical variable name.
* **`unit`** (`String`): Physical unit (`°C`, `kPa`, `kscmh`, `kg/h`).
* **`normal_min`** / **`normal_max`** / **`normal_mean`** (`Float`): Nominal operating parameters.

### `:FailureMode`
Represents operational disturbances and equipment faults (TEP IDV 1-21).
* **`id`** (`String`, Unique): E.g., `IDV_4`.
* **`code`** (`String`, Indexed): Benchmark code, e.g., `IDV(4)`.
* **`name`** (`String`): Disturbance title.
* **`category`** (`String`): Feed Disturbance, Cooling Disturbance, Actuator Mechanical Failure, Kinetic Drift.
* **`severity`** (`String`): `Low`, `Medium`, `High`, `Critical`.
* **`description`** (`String`): Physical origin and mechanism of the failure.

---

## 2. Relationship Types

| Relationship | Start Node | End Node | Properties | Description / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `FEEDS` | `:Unit` | `:Unit` | `stream: String`, `phase: String`, `description: String` | Directed material and energy flow between process units. |
| `MEASURES` | `:Sensor` | `:Unit` | - | Associates sensor instrumentation with monitored equipment. |
| `SUSCEPTIBLE_TO` | `:Unit` | `:FailureMode` | - | Specifies physical vulnerability of equipment to failure modes. |
| `TYPICALLY_CAUSES` | `:FailureMode` | `:FailureMode` | `mechanism: String`, `delay_sec: Int` | Directed domino/cascading causal chain between faults. |
| `MANIFESTS_IN` | `:FailureMode` | `:Sensor` | `expected_deviation: String`, `metric: String` | Sensor departures triggered by this disturbance. |

---

## 3. Cypher Constraints & Indexes
```cypher
// Uniqueness constraints
CREATE CONSTRAINT unit_id_unique IF NOT EXISTS FOR (u:Unit) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS FOR (s:Sensor) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT failure_mode_id_unique IF NOT EXISTS FOR (f:FailureMode) REQUIRE f.id IS UNIQUE;

// Performance lookup indexes
CREATE INDEX sensor_tag_idx IF NOT EXISTS FOR (s:Sensor) ON (s.tag);
CREATE INDEX sensor_var_idx IF NOT EXISTS FOR (s:Sensor) ON (s.variable_name);
CREATE INDEX failure_code_idx IF NOT EXISTS FOR (f:FailureMode) ON (f.code);
CREATE INDEX unit_name_idx IF NOT EXISTS FOR (u:Unit) ON (u.name);
```

---

## 4. Viva Explanations for Knowledge Graph Design

1. **Why directed `[:FEEDS]` relationships?**
   Chemical plants follow conservation of mass and thermodynamics. When reactor temperature rises, the thermal perturbation propagates downstream to the condenser via Stream 7. Directed edges allow Graph Traversal and Hop Distance algorithms to enforce physical flow directionality.

2. **Why `[:TYPICALLY_CAUSES]` between failure modes?**
   Industrial faults rarely remain isolated. For example, cooling water loss (`IDV(4)`) causes jacket heat transfer exhaustion, which subsequently drives the cooling control valve into continuous saturation or mechanical sticking (`IDV(11)`). Modeling cascading relationships enables compound explanation generation by the RCA agent.

3. **Why map `[:MANIFESTS_IN]` to sensors?**
   Gives the agent a bi-directional index:
   - Given anomalous sensors $\to$ find candidate root causes.
   - Given a hypothesized root cause $\to$ verify if all expected manifesting sensors actually deviated in the telemetry window.
