export const submitQuery = async (userQuery, debug = false) => {
  try {
    const response = await fetch("http://localhost:5000/component-orchestrator/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: userQuery,
        debug: debug,
      }),
    });

    const result = await response.json();

    if (debug && result.execution_trace) {
      console.log("Execution trace (dev only):", result.execution_trace);
    }

    return result.final_response || result.error;
  } catch (err) {
    console.error("Error in submitQuery:", err);
    return "An error occurred.";
  }
};