import http from "k6/http";

export default function () {
  const payload = JSON.stringify({
    email: "neelu.encircle@gmail.com",
    password: "Neel@123",
    rememberMe: true,
  });

  const res = http.post(
    "https://epms-app.encircledev.com/api/v1/auth/login",
    payload,
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  console.log(res.status);
  console.log(res.body);
}