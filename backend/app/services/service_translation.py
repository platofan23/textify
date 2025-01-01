import requests
import json

url = "http://localhost:55000/translate"
payload = {
    "q": (
        "In der alten Hafenstadt Levanthor herrschte an jenem Samstagmorgen eine eigenartige Spannung in der Luft. Obwohl die Sonne noch kaum über den Horizont lugte, hatten sich schon etliche Menschen auf dem großen Marktplatz eingefunden, um bei den Vorbereitungen für das alljährliche Lichterfest zu helfen. Holzkarren standen kreuz und quer, beladen mit bunten Lampions, kunstvollen Papierlaternen und Kisten voller Kerzen. Händler aus den umliegenden Dörfern rollten ihre Handwagen heran, um exotische Gewürze, frisch geflochtene Körbe und kunstvoll gefertigte Tonwaren anzubieten."
        "Der Geruch von Meersalz mischte sich mit dem Duft von gebratenen Zwiebeln und süßem Gebäck, das in kleinen, dampfenden Wagen feilgeboten wurde. Auf einer provisorisch errichteten Bühne probte eine Gruppe Musiker ihre Stücke, begleitet vom leisen Klappern der Möwen, die über dem Hafenbecken kreisten. In der Ferne läuteten die Glocken des Leuchtturms, um ankommende Fischerboote vor den Untiefen zu warnen."
        "Während sich die ersten Sonnenstrahlen über die rotgedeckten Dächer der alten Speicherhäuser zogen, schwirrten bereits Hunderte von Laternen in den Händen der Stadtbewohner umher. Jeder wollte rechtzeitig fertig werden, bevor die Dunkelheit eintrat. Denn wenn die Dämmerung kam, sollte Levanthor in einem Meer aus Lichtern erstrahlen – ein Schauspiel, auf das man sich das ganze Jahr über freute. Sobald die Lampions und Kerzen am Abend entzündet würden, sollte die Stadt in schimmerndem Gold getaucht sein. Reisende erzählten sich, dass man das Leuchten schon von den Hügeln weit hinter der Küste aus sehen konnte."
        "So eilte jeder geschäftig umher: Kinder liefen kichernd zwischen den Ständen hindurch, die Marktfrauen feilten an ihren Preisen, und ein alter Seemann erzählte lauthals abenteuerliche Geschichten von seiner letzten Reise ins Südmeer. Doch trotz der Geschäftigkeit lag eine gewisse Vorfreude in der Luft, die jeden ansteckte. Die Einwohner liebten ihr Fest, das ihnen seit Jahrzehnten Kraft und Gemeinschaftssinn gab. Und so konnte man bereits am frühen Tag spüren, dass dieser Abend noch lange in Erinnerung bleiben würde – nicht nur für die Menschen von Levanthor, sondern auch für all jene Besucher, die sich von diesem flirrenden Lichterspektakel in ihren Bann ziehen ließen."
    ),
    "source": "de",
    "target": "en",
    "format": "text",
    "alternatives": 3,
    "api_key": ""
}

headers = {"Content-Type": "application/json"}

# POST-Anfrage senden
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Die Antwort als JSON ausgeben
# Beachte, dass man response.json() normalerweise nur einmal aufrufen kann,
# da der Stream nach dem ersten Aufruf verbraucht ist.
result = response.json()
print(result)
