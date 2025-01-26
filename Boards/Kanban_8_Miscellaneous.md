<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<h1>Kanban Board</h1>
<h2>Miscellaneous</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
      <th>Importance 1(very low) .. 5(very high)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Create `config.ini`</td>
      <td>Create a configuration file `config.ini` for managing application settings.</td>
      <td>
        - Contains sections for REST API, database, translation, caching, and logging.<br>
        - Includes default values and placeholders for sensitive information.<br>
        - Validates successfully using the ConfigManager class.
      </td>
      <td>Done</td>
      <td>CJ</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Implement Config Class</td>
      <td>Develop a class to manage configuration file parsing and validation.</td>
      <td>
        - Can read `config.ini`.<br>
        - Provides methods to fetch configuration values.<br>
        - Includes validation for required sections and keys.
      </td>
      <td>Done</td>
      <td>JK</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Write Dockerfile for CPU Environment</td>
      <td>Develop a Dockerfile for deploying the application in a CPU-based environment.</td>
      <td>
        - Installs all dependencies required for a CPU-only setup.<br>
        - Uses a lightweight base image.<br>
        - Includes proper CMD/ENTRYPOINT for running the application.
      </td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Write Dockerfile for GPU Environment</td>
      <td>Develop a Dockerfile for deploying the application in a GPU-accelerated environment.</td>
      <td>
        - Based on NVIDIA's CUDA image.<br>
        - Includes dependencies like PyTorch with GPU support.<br>
        - Properly configured to use `nvidia-container-runtime`.
      </td>
      <td>Done</td>
      <td>JK</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Create `docker-compose.yml`</td>
      <td>Create a `docker-compose.yml` file to manage application services.</td>
      <td>
        - Includes definitions for application, database, and other required services.<br>
        - Supports CPU and GPU configurations via profiles or environment variables.<br>
        - Configures volume mounts and environment variables.
      </td>
      <td>Done</td>
      <td>JK</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Choose a Deployment Method</td>
      <td>Evaluate and select an appropriate deployment method (e.g., Kubernetes, Docker Swarm).</td>
      <td>
        - List of pros/cons for each method.<br>
        - Documented deployment steps for the chosen method.<br>
        - Verified deployment on the target environment.
      </td>
      <td>Done</td>
      <td>ALL</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Implement Database Class</td>
      <td>Develop a class to manage database interactions.</td>
      <td>
        - Includes methods for CRUD operations.<br>
        - Handles connection pooling and reconnections.<br>
        - Includes error handling and logging.
      </td>
      <td>In Progress</td>
      <td>JK, CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Implement Logger Class</td>
      <td>Create a reusable logging class for the application.</td>
      <td>
        - Supports multiple log levels (e.g., INFO, WARNING, ERROR).<br>
        - Configurable output to console and file.<br>
        - Includes options for structured logging.
      </td>
      <td>Done</td>
      <td>CJ</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Implement Cache Class</td>
      <td>Develop a cache manager class for in-memory caching with persistence.</td>
      <td>
        - Uses File caching with configurable size.<br>
        - Supports serialization and deserialization for persistence.<br>
        - Includes methods to clear, save, and load cache.
      </td>
      <td>Done</td>
      <td>JK</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</body>
</html>
