import httpx
import os

# LTA DataMall Endpoint for Traffic Incidents
TRAFFIC_INCIDENTS_URL = (
    "https://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
)


def singapore_traffic() -> str:
    """
    Returns real-time traffic incidents in Singapore using LTA DataMall API.
    API Reference: http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents

    Requires LTA_DATAMALL_KEY to be set in environment variables.
    """

    # read API_KEY from environment variable
    api_key = os.environ.get("LTA_DATAMALL_KEY")

    if not api_key:
        return "Error: LTA_DATAMALL_KEY not found in environment variables."

    headers = {"AccountKey": api_key, "accept": "application/json"}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(TRAFFIC_INCIDENTS_URL, headers=headers)
            response.raise_for_status()
            data = response.json()

            incidents = data.get("value", [])

            if not incidents:
                return "Current Traffic Status: All roads are clear. No major incidents reported."

            result = "Real-time Traffic Incidents in Singapore:\n"

            # to avoid overwhelming the output, we will limit to the first 8 incidents and indicate if there are more
            for i, incident in enumerate(incidents[:8], 1):
                msg = incident.get("Message", "No description available")
                result += f"{i}. {msg}\n"

            if len(incidents) > 8:
                result += f"... and {len(incidents) - 8} more incidents reported."

            return result.strip()

    except httpx.HTTPStatusError as e:
        return f"Error: Unable to fetch traffic data (HTTP {e.response.status_code})."
    except Exception as e:
        return (
            f"Error: An unexpected error occurred while fetching traffic news: {str(e)}"
        )


if __name__ == "__main__":
    print(singapore_traffic())
