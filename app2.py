from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

from state_code import state_data

app = Flask(__name__)

def case_pendency_data_dist(dist):
    if dist in state_data.keys():
        url = (f"https://njdg.ecourts.gov.in/njdgnew/?p=main/index&state_code={state_data[dist]}")
    else:
        url = "https://njdg.ecourts.gov.in/njdgnew/?p=main/index"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "example"})  # Update with actual id/class
        
        if table:
            rows = table.find_all("tr")
            data = []
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])  # Get rid of empty values
            return data
        else:
            return {"error": "Unable to find the data table on NJDG"}
    else:
        return {"error": "Failed to retrieve data from NJDG"}

def case_pendency_data_high():
    url = "https://njdg.ecourts.gov.in/hcnjdgnew/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "example"})  # Update with actual id/class
        
        if table:
            rows = table.find_all("tr")
            data = []
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])  # Get rid of empty values
            return data
        else:
            return {"error": "Unable to find the data table on NJDG"}
    else:
        return {"error": "Failed to retrieve data from NJDG"}

def convert_to_dict(data):
    result = {}
    for row in data:
        if len(row) > 1:
            key = f"{row[0]} {row[1]}"
            value = row[2:]
            result[key] = value
    return result

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    intent = req.get('queryResult').get('intent').get('displayName')
    parameters = req.get('queryResult').get('parameters')
    
    if intent == 'pending-case.selected-dist-court':
        dist = parameters.get('geo-state')
        case_pendency_data = case_pendency_data_dist(dist)
        
        if isinstance(case_pendency_data, dict) and 'error' in case_pendency_data:
            return jsonify({"fulfillmentText": case_pendency_data['error']})
        
        result_dict = convert_to_dict(case_pendency_data)
        response_text = ""
        
        for key, value in result_dict.items():
            response_text += f"{key}: {', '.join(value)}\n"
        
        return jsonify({"fulfillmentText": response_text})
    
    elif intent == 'pending-case.selected-high-court':
        # Implement similar logic for handling high court cases
        case_pendency_data = case_pendency_data_high()
        
        if isinstance(case_pendency_data, dict) and 'error' in case_pendency_data:
            return jsonify({"fulfillmentText": case_pendency_data['error']})
        
        result_dict = convert_to_dict(case_pendency_data)
        response_text = ""
        
        for key, value in result_dict.items():
            response_text += f"{key}: {', '.join(value)}\n"
        
        return jsonify({"fulfillmentText": response_text})
    
    else:
        return jsonify({"fulfillmentText": "Sorry, I didn't understand that intent."})

return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
