from google.genai import types
print("Part.from_bytes:", hasattr(types.Part, "from_bytes"))
try:
    part = types.Part.from_bytes(data=b"123", mime_type="image/jpeg")
    print("Part works:", part)
except Exception as e:
    print("Part error:", e)

try:
    content = types.Content(role="user", parts=[part])
    print("Content works:", content)
except Exception as e:
    print("Content error:", e)
