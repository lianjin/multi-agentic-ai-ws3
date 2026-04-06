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

    # 从环境变量获取 API Key
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

            # 格式化输出结果
            result = "Real-time Traffic Incidents in Singapore:\n"

            # 为了避免 Agent 接收过长信息，通常取前 5-8 条最重要的信息
            # 每条数据包含 Type (事故/施工等) 和 Message (具体地点和描述)
            for i, incident in enumerate(incidents[:8], 1):
                msg = incident.get("Message", "No description available")
                # LTA 的 Message 通常形如 "(12/5)18:30 Accident on PIE (towards Changi)..."
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
