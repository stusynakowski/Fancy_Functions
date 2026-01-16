# Implementation Plan: Fancy Cells (Spec 001)

## Overview
This plan covers the implementation of the atomic data unit (`FancyCell`) and the storage layer (`DatumStore`) as defined in `docs/spec/001-fancy-cells.md`.

## 1. Class: `FancyCell`
**File:** `src/fancy_core/cells.py`

### 1.1 Data Model
- [x] Define `StorageKind` Enum: `VALUE`, `REFERENCE`, `COMPOSITE`.
- [x] Define `FancyCell` Pydantic Model:
    - `id`: UUID (default factory)
    - `alias`: str
    - `type_hint`: str (default "Any")
    - `storage_kind`: StorageKind
    - `value`: Any (for VALUE/COMPOSITE)
    - `reference_uri`: str (for REFERENCE)
    - `reference_meta`: Dict (metadata for REFERENCE)

### 1.2 Factory Methods
- [x] `create_value(value, alias, type_hint)` -> Kind: VALUE
- [x] `create_reference(uri, alias, type_hint, meta)` -> Kind: REFERENCE
- [x] `create_composite(children, alias)` -> Kind: COMPOSITE

## 2. Abstraction: `DatumStore` (The Physics)
**File:** `src/fancy_core/store.py`

### 2.1 Interface
- [x] Abstract Base Class `DatumStore`.
- [x] Method `resolve(cell: FancyCell) -> Any`:
    - Logic to return `value` if direct.
    - Logic to load from `reference_uri` if reference.
    - Logic to resolve/unpack if composite.
- [x] Method `put(value: Any, alias: str) -> FancyCell`:
    - Logic to persist object and return a new Cell.

### 2.2 Implementation: `InMemoryStore`
- [x] Internal Dict `_data` to map URI -> Object.
- [x] Implement `put` generating `memory://{uuid}` URIs.
- [x] Implement `resolve` fetching from dict.

## 3. Testing
**File:** `tests/test_cells.py`
- [x] Test cell creation (all 3 modes).
- [x] Test `InMemoryStore` round-trip (put then resolve).
- [x] Test error handling for missing references.
