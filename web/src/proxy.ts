import { NextResponse, type NextRequest } from "next/server";

// WLDD-only prototype: any page without the session cookie goes to /login (SPEC, Login). Not real auth.
export function proxy(request: NextRequest) {
  if (!request.cookies.get("truerate_session")) {
    const url = new URL("/login", request.url);
    url.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
}

export const config = {
  matcher: ["/((?!login|_next/static|_next/image|favicon.ico).*)"],
};
