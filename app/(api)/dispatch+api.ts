import goddesses from "@/lib/goddess_truecodes.json";

export async function GET(request: Request) {
  try {
    const randomIndex = Math.floor(Math.random() * goddesses.length);
    const randomGoddess = goddesses[randomIndex];

    return Response.json({ data: randomGoddess });
  } catch (error) {
    console.error("Error dispatching goddess:", error);
    return Response.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
