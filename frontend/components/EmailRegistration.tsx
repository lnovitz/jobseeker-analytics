"use client";

import React, { useState, useEffect } from "react";
import { PublicClientApplication } from "@azure/msal-browser";

import { CopyIcon, EmailIcon, ArrowRightIcon, CheckIcon, SendIcon } from "@/components/icons";

type Step = "email" | "otp" | "success" | "test";
type EmailProvider = "gmail" | "outlook" | "other";
type TestStatus = "not_started" | "pending" | "success" | "error";

const GMAIL_CLIENT_ID = process.env.NEXT_PUBLIC_GMAIL_CLIENT_ID || "your-gmail-client-id";
const OUTLOOK_CLIENT_ID = process.env.NEXT_PUBLIC_OUTLOOK_CLIENT_ID || "your-outlook-client-id";

const msalConfig = {
	auth: {
		clientId: OUTLOOK_CLIENT_ID,
		authority: "https://login.microsoftonline.com/common",
		redirectUri: typeof window !== "undefined" ? window.location.origin : ""
	}
};

const msalInstance = typeof window !== "undefined" ? new PublicClientApplication(msalConfig) : null;

export function EmailRegistration() {
	const [email, setEmail] = useState("");
	const [otp, setOtp] = useState("");
	const [currentStep, setCurrentStep] = useState<Step>("email");
	const [trackingEmail, setTrackingEmail] = useState("");
	const [copied, setCopied] = useState(false);
	const [emailProvider, setEmailProvider] = useState<EmailProvider>("other");
	const [testStatus, setTestStatus] = useState<TestStatus>("not_started");
	const [testEmailReceived, setTestEmailReceived] = useState(false);

	useEffect(() => {
		// Load Google API Client
		const script = document.createElement("script");
		script.src = "https://apis.google.com/js/api.js";
		script.onload = () => {
			window.gapi.load("client:auth2", initGoogleClient);
		};
		document.body.appendChild(script);

		// Initialize MSAL
		msalInstance?.initialize();
	}, []);

	const initGoogleClient = () => {
		window.gapi.client.init({
			clientId: GMAIL_CLIENT_ID,
			scope: "https://www.googleapis.com/auth/gmail.settings.basic"
		});
	};

	const detectEmailProvider = (email: string) => {
		if (email.toLowerCase().endsWith("@gmail.com")) {
			return "gmail";
		} else if (
			email.toLowerCase().endsWith("@outlook.com") ||
			email.toLowerCase().endsWith("@hotmail.com") ||
			email.toLowerCase().endsWith("@live.com")
		) {
			return "outlook";
		}
		return "other";
	};

	const validateEmail = (email: string) => {
		return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
	};

	const handleEmailSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (validateEmail(email)) {
			setEmailProvider(detectEmailProvider(email));
			setCurrentStep("otp");
		}
	};

	const handleOtpSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (otp.length === 6) {
			const token = Math.random().toString(36).substring(7);
			setTrackingEmail(`track+${token}@track.jobba.help`);
			setCurrentStep("success");
		}
	};

	const setupGmailForwarding = async () => {
		try {
			setTestStatus("pending");
			const response = await window.gapi.auth2.getAuthInstance().signIn();
			if (response) {
				// Set up Gmail filter
				const filter = {
					criteria: {
						from: "*@*.com",
						subject: "job OR position OR application OR interview OR opportunity"
					},
					action: {
						forward: trackingEmail
					}
				};

				await window.gapi.client.gmail.users.settings.filters.create({
					userId: "me",
					resource: filter
				});
				setCurrentStep("test");
			}
		} catch (error) {
			console.error("Error setting up Gmail forwarding:", error);
			setTestStatus("error");
		}
	};

	const setupOutlookForwarding = async () => {
		try {
			setTestStatus("pending");
			if (!msalInstance) {
				throw new Error("MSAL instance not initialized");
			}
			const response = await msalInstance.loginPopup({
				scopes: ["Mail.ReadWrite"]
			});

			if (response) {
				// Set up Outlook rule
				const rule = {
					displayName: "Jobba Job Application Tracking",
					sequence: 1,
					isEnabled: true,
					conditions: {
						subjectContains: ["job", "position", "application", "interview", "opportunity"]
					},
					actions: {
						forwardTo: [
							{
								emailAddress: {
									address: trackingEmail
								}
							}
						]
					}
				};

				// The actual API call would go here
				console.log("Setting up Outlook rule:", rule);
				setCurrentStep("test");
			}
		} catch (error) {
			console.error("Error setting up Outlook forwarding:", error);
			setTestStatus("error");
		}
	};

	const sendTestEmail = async () => {
		setTestStatus("pending");
		try {
			// Simulate sending a test email
			// In production, this would be an API call to your backend
			await new Promise((resolve) => setTimeout(resolve, 2000));

			// Start polling for the test email
			pollForTestEmail();
		} catch (error) {
			console.error("Error sending test email:", error);
			setTestStatus("error");
		}
	};

	const pollForTestEmail = () => {
		let attempts = 0;
		const maxAttempts = 30; // Poll for 1 minute (2-second intervals)

		const poll = setInterval(async () => {
			attempts++;

			try {
				// In production, this would be an API call to check if the email was received
				// For demo purposes, we'll simulate success after 4 seconds
				if (attempts === 2) {
					setTestEmailReceived(true);
					setTestStatus("success");
					clearInterval(poll);
				}
			} catch (error) {
				console.error("Error polling for test email:", error);
			}

			if (attempts >= maxAttempts) {
				setTestStatus("error");
				clearInterval(poll);
			}
		}, 2000);
	};

	const copyToClipboard = async () => {
		await navigator.clipboard.writeText(trackingEmail);
		setCopied(true);
		setTimeout(() => setCopied(false), 2000);
	};

	return (
		<div className="w-full max-w-md mx-auto p-6 space-y-8">
			{currentStep === "email" && (
				<form className="space-y-6" onSubmit={handleEmailSubmit}>
					<div>
						<h2 className="text-2xl font-bold text-gray-900 mb-4">Get Started</h2>
						<p className="text-gray-600 mb-6">Enter your email to start tracking your job applications</p>
					</div>
					<div>
						<label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="email">
							Email address
						</label>
						<div className="relative">
							<EmailIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
							<input
								required
								className="pl-10 w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
								id="email"
								placeholder="you@example.com"
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
							/>
						</div>
					</div>
					<button
						className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
						type="submit"
					>
						Continue
						<ArrowRightIcon className="h-4 w-4" />
					</button>
				</form>
			)}

			{currentStep === "otp" && (
				<form className="space-y-6" onSubmit={handleOtpSubmit}>
					<div>
						<h2 className="text-2xl font-bold text-gray-900 mb-4">Verify your email</h2>
						<p className="text-gray-600 mb-6">We've sent a 6-digit code to {email}</p>
					</div>
					<div>
						<label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="otp">
							Enter verification code
						</label>
						<input
							required
							className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-center tracking-widest"
							id="otp"
							placeholder="000000"
							type="text"
							value={otp}
							onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
						/>
					</div>
					<button
						className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
						disabled={otp.length !== 6}
						type="submit"
					>
						Verify
					</button>
				</form>
			)}

			{currentStep === "success" && (
				<div className="space-y-6">
					<div>
						<h2 className="text-2xl font-bold text-gray-900 mb-4">You're all set!</h2>
						<p className="text-gray-600 mb-6">Use this email address to forward your job-related emails:</p>
					</div>
					<div className="relative">
						<input
							readOnly
							className="w-full rounded-lg border border-gray-300 px-4 py-2 pr-10 bg-gray-50"
							type="text"
							value={trackingEmail}
						/>
						<button
							className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
							title="Copy to clipboard"
							onClick={copyToClipboard}
						>
							{copied ? (
								<CheckIcon className="h-5 w-5 text-green-500" />
							) : (
								<CopyIcon className="h-5 w-5" />
							)}
						</button>
					</div>
					{emailProvider === "gmail" && (
						<div className="bg-blue-50 p-4 rounded-lg">
							<p className="text-sm text-blue-800">
								We've detected you're using Gmail. Would you like to set up automatic forwarding?
							</p>
							<button
								className="mt-3 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
								onClick={setupGmailForwarding}
							>
								Set up Gmail forwarding
							</button>
						</div>
					)}
					{emailProvider === "outlook" && (
						<div className="bg-blue-50 p-4 rounded-lg">
							<p className="text-sm text-blue-800">
								We've detected you're using Outlook. Would you like to set up automatic forwarding?
							</p>
							<button
								className="mt-3 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
								onClick={setupOutlookForwarding}
							>
								Set up Outlook forwarding
							</button>
						</div>
					)}
				</div>
			)}

			{currentStep === "test" && (
				<div className="space-y-6">
					<div>
						<h2 className="text-2xl font-bold text-gray-900 mb-4">Let's Test the Setup</h2>
						<p className="text-gray-600 mb-6">
							We'll send a test email to verify everything is working correctly.
						</p>
					</div>

					{testStatus === "not_started" && (
						<button
							className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
							onClick={sendTestEmail}
						>
							Send Test Email
							<SendIcon className="h-4 w-4" />
						</button>
					)}

					{testStatus === "pending" && (
						<div className="text-center">
							<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4" />
							<p className="text-gray-600">
								{testEmailReceived ? "Email received! Verifying setup..." : "Sending test email..."}
							</p>
						</div>
					)}

					{testStatus === "success" && (
						<div className="bg-green-50 p-4 rounded-lg">
							<div className="flex items-center gap-2 text-green-800 mb-2">
								<CheckIcon className="h-5 w-5" />
								<p className="font-medium">Setup Complete!</p>
							</div>
							<p className="text-sm text-green-700">
								The test email was successfully forwarded. You're ready to start tracking your job
								applications!
							</p>
						</div>
					)}

					{testStatus === "error" && (
						<div className="bg-red-50 p-4 rounded-lg">
							<p className="text-sm text-red-800">
								There was an error testing the setup. Please try again or contact support if the issue
								persists.
							</p>
							<button
								className="mt-3 w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
								onClick={sendTestEmail}
							>
								Retry Test
							</button>
						</div>
					)}
				</div>
			)}
		</div>
	);
}
