// ==============================================================================
// Neo4j Schema Constraints and Performance Indexes for TEP Knowledge Graph
// Ensures data integrity and fast traversal across Units, Sensors, and Failure Modes
// ==============================================================================

// --- Uniqueness Constraints ---
CREATE CONSTRAINT unit_id_unique IF NOT EXISTS
FOR (u:Unit) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT failure_mode_id_unique IF NOT EXISTS
FOR (f:FailureMode) REQUIRE f.id IS UNIQUE;

CREATE CONSTRAINT equipment_id_unique IF NOT EXISTS
FOR (e:Equipment) REQUIRE e.id IS UNIQUE;

// --- Performance Indexes ---
CREATE INDEX unit_name_idx IF NOT EXISTS
FOR (u:Unit) ON (u.name);

CREATE INDEX sensor_tag_idx IF NOT EXISTS
FOR (s:Sensor) ON (s.tag);

CREATE INDEX failure_code_idx IF NOT EXISTS
FOR (f:FailureMode) ON (f.code);
