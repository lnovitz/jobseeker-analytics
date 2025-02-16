export default function RedirectUrl(env: string): string {
	if (env == "PROD") {
		return "https://jobseeker-analytics.onrender.com";
	} else {
		return "http://localhost:8000";
	}
}
