const BASE_API = import.meta.env.VITE_API_URL;

export interface LoginResult {
  access_token: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<LoginResult> {
  const response = await fetch(`${BASE_API}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} - ${errorText}`);
  }

  return response.json();
}
