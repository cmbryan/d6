# d6

A battle simulator for tabletop dice gaming

## Usage

1. **Run the Flask application**:

   ```bash
   poetry run python src/app.py
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://127.0.0.1:5000`.

3. **Simulate an attack**:
   Use the provided endpoints to select units and simulate attacks. Refer to the API documentation for details on the available routes and parameters.

## API Documentation

- **POST /simulate_attack**: Simulates an attack between two units.
  - **Request Body**:

    ```json
    {
      "attacker": "Attacker Unit Name",
      "defender": "Defender Unit Name"
    }
    ```

  - **Response**:

    ```json
    {
      "result": "Damage inflicted",
      "details": {
        "hits": "Number of hits",
        "wounds": "Number of wounds",
        "saved_wounds": "Number of wounds saved"
      }
    }
    ```
