# Fancy Functions Framework: Conceptual Overview

# background how can we perform super technical operations and processes in the same way users perform operations in excel
# better motivation... how can we perform really sophisticated operations at scale in a way that is as easy as making a funtion in excel

# consider the problem of mining and structureing data from a youtube video in a way that we visalize and easily the data analysis process


# usecase problem.
# i have a problem where I have a youtube chanel containing videos
# of people asking servey questions.
# from this youtube video I want to create a set of tables
# i first extract the list of videos 
# i thinen make a model that extracts the meta data corresponding to the video
# i then stranscribe the video
# i then need to partition the video by conversation
# then need to analyze each conversation and mapt that to meta data of interest.
# from this use table. i want to perform wholistic analysis on this video.
# 
# and i want to convert this use




## Vision
To create a workflow system where data handling, processing, and execution are generalized and observable, like in spreadsheets, regardless of how complicated the data or the function is. By wrapping data and operations, we can stage, visualize, and manage complex data transformations before during and after execution.
    
## Core Concepts

### 1. Cell
**Definition:** A generic wrapper for a unit of data.
*   **Purpose:** To serve as a unit of data that is easy for users to understand that contains data that is processed, staged for processing, or currently being generated.
*   **Capabilities:**
    *   Holds actual values or represents "potential" data (placeholders/staging) where it is defined by the output, could map to the ouput of a fundction, 
    *   Maintains state: knows if it contains a value or is empty or staged.
        it notes where its contents come from (like a fancy_function)
    *   Tracks provenance: knows how it was created. if it is staged
*   **Value:** Essential for staging the workflow graph and monitoring data state during processing.

### 2. Fancy Function
**Definition:** A specialized function capable of operating on Cells 
*   **Mechanism:** created by decorating a standard function any user could define in python
*   **Behavior:**
    *   Maps input Cells to output Cells. (but typically a one to one correspondance)
    *   Generates placeholder Cells (future data) during the staging phase.
    *   Decouples the logic from the raw data, allowing operations on the "idea" of the data. can be abstracted a way
    it means you can define a place holder for outputs.
    

    WHY do we want to do this? I want a user experience to be able to easily define functions as they would any function in spread sheet software. if it is quick to compute we can execute and populate the output cells with the updated value provided the input cells contain proper input. if the function is really computationally expensive or, if the input data is staged but no value is contained we can we can say that the output is from this argument and we will execute at a later time. even though the cell has not produced an output it still produces a cell that will denote (its contents will contain the output from the corredpondingg cell)
    so if i decorate a function with the fancy function operator. I can start to stage processes. I can also manage the execution. like run when you have the correct input data is provided. wait until the users expicitly chooses to execute.


    

    
### 3. Step
**Definition:** A Step is a collection of cells and their mappings to fancy functions Fancy Functions and how they are executed/orchestrated.
*   **Role:** it defines a meaningul process/processes the user is able to comprend and abstract.  Defines which cells  fancy_functions  applied to data (the generalization of the process). consider the problem we are appliying a function iteriavely across 10 cells to produce 100 cells.  or 100 rows or a 1000 rows. the step remains the same. but number of cells and the contents of the cells we need to perform may change but the general processes remainds the same
*   **Execution Patterns:**
    *   Can apply a function iteratively (e.g., row-wise operation like a for-loop).
    *   Can handle functions where the cells for the function are changing or number of cels change
*   **Example:** Applying a "compute average" function across a list of numerical Cells,when new data is coming. 
    
    the user will be able to manage the collections of functions and cells as a whole. if they decidee.  


# is is an abstraction of a function being applied. people know what they are getting from a given process.

### 4. Workflow
**Definition:** The high-level manager of Steps. it is a collection of steps the user defines to denote some meaningful process.
*   **Purpose:** To organize the order of execution, to manage steps.
*   **Features:**
    *  
    *   "Stages" the table/graph before actual execution, and its current   state.
    *   Manages the flow of data from one Step to the next.
    can be easily serialized, to be shared with others. 

## Example Flow

1.  **Ingest:** Start with a simple table of data.
2.  **Wrap:** Wrap individual data points in **Cells**.
3.  **Define Logic:** Create **Fancy Functions** (e.g., `calculate_metrics`, `fetch_website`).
4.  **Orchestrate:** Define **Steps** that apply these functions to the Cells (e.g., "Iterate `calculate_metrics` over `Column A`").
    *   *Visual:* `Cell1` -> `Function1`, `Cell2` -> `Function1`, etc.
5.  **Execute:** The **Workflow** runs the steps, populating placeholder Cells with actual results.





