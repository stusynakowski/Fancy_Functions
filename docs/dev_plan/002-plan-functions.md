# Implementation Plan: Fancy Functions (Spec 002)

## Overview
This plan covers the implementation of the `FancyFunction` metadata, the Registry, and the `@step` decorator as defined in `docs/spec/002-fancy-functions.md`.

## 1. Class: `FancyFunction`
**File:** `src/fancy_core/functions.py`

### 1.1 Data Model
- [ ] Define `FancyFunction` Pydantic Model:
    - `slug`: str
    - `name`: str
    - `description`: str
    - `input_contract`: `Dict[str, Type]` (or string representation of type)
    - `output_contract`: `Dict[str, Type]`
    - `_executable`: Private field to hold actual callable.

## 2. Component: `FunctionRegistry`
**File:** `src/fancy_core/registry.py`

### 2.1 Logic
- [ ] Singleton or module-level dict: `_REGISTRY: Dict[str, FancyFunction]`.
- [ ] `register(func_def: FancyFunction)` method.
- [ ] `get(slug: str) -> FancyFunction` method.

## 3. The Decorator: `@step`
**File:** `src/fancy_core/decorators.py`

### 3.1 Introspection Logic
- [ ] Use `inspect` module to parse signature of decorated function.
- [ ] Extract argument names and type hints for `input_contract`.
- [ ] Extract return annotation for `output_contract`.

### 3.2 Wrapping Logic (The Factory Pattern)
- [ ] **Crucial:** The decorated function, when called, must NOT run the code.
- [ ] It must accept `FancyCell` objects as arguments.
- [ ] It must return a `WorkflowStep` (defined in Spec 003) + Output Wrappers.
    *   *Dependency:* Requires `WorkflowStep` definition (Plan 003).
    *   * interim:* Return a temporary `StepWiring` object if 003 is not ready, or implement concurrently.

## 4. Testing
**File:** `tests/test_functions.py`
- [ ] Define a sample function `add_cols(df, col)`.
- [ ] Decorate with `@step`.
- [ ] Verify functionality is registered in `FunctionRegistry`.
- [ ] Verify `input_contract` matches signature.
