# Implementation Plan: Fancy Cells (Spec 001)

## Overview
This plan covers the implementation of the atomic data unit (`FancyCell`) and the storage layer (`DatumStore`) as defined in `docs/spec/001-fancy-cells.md`.

## 1. Class: `FancyCell`
**File:** `src/fancy_core/cells.py`

### 1.1 Data Model
- [ ] Define `StorageKind` Enum: `VALUE`, `REFERENCE`, `COMPOSITE`.
- [ ] Define `FancyCell` Pydantic Model:
    - `id`: UUID (default factory)
    - `alias`: str
    - `type_hint`: str (default "Any")
    - `storage_kind`: StorageKind
    - `value`: Any (for VALUE/COMPOSITE)
    - `reference_uri`: str (for REFERENCE)
    - `reference_meta`: Dict (metadata for REFERENCE)

### 1.2 Factory Methods
- [ ] `create_value(value, alias, type_hint)` -> Kind: VALUE
- [ ] `create_reference(uri, alias, type_hint, meta)` -> Kind: REFERENCE
- [ ] `create_composite(children, alias)` -> Kind: COMPOSITE

## 2. Abstraction: `DatumStore` (The Physics)
**File:** `src/fancy_core/store.py`

### 2.1 Interface
- [ ] Abstract Base Class `DatumStore`.
- [ ] Method `resolve(cell: FancyCell) -> Any`:
    - Logic to return `value` if direct.
    - Logic to load from `reference_uri` if reference.
    - Logic to resolve/unpack if composite.
- [ ] Method `put(value: Any, alias: str) -> FancyCell`:
    - Logic to persist object and return a new Cell.

### 2.2 Implementation: `InMemoryStore`
- [ ] Internal Dict `_data` to map URI -> Object.
- [ ] Implement `put` generating `memory://{uuid}` URIs.
- [ ] Implement `resolve` fetching from dict.

## 3. Testing
**File:** `tests/test_cells.py`
- [ ] Test cell creation (all 3 modes).
- [ ] Test `InMemoryStore` round-trip (put then resolve).
- [ ] Test error handling for missing references.
