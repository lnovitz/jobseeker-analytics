"use client";
import Head from "next/head";
import { useState, useRef, useEffect } from "react";
import ReCAPTCHA from "react-google-recaptcha";

export default function Home() {
	// Form state
	const [email, setEmail] = useState("");
	const [isChecked, setIsChecked] = useState(false);
	const [errorMessage, setErrorMessage] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [formSubmitted, setFormSubmitted] = useState(false);

	// Dark mode detection
	const [isDarkMode, setIsDarkMode] = useState(false);

	// ReCAPTCHA reference
	const recaptchaRef = useRef<ReCAPTCHA>(null);

	// Check for dark mode on mount
	useState(() => {
		if (typeof window !== "undefined") {
			const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
			setIsDarkMode(isDark);
		}
	});

	// Mobile-specific adjustments for ReCAPTCHA
	useEffect(() => {
		const handleRecaptchaOnMobile = () => {
			if (typeof window !== "undefined") {
				// Check if mobile
				const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

				if (isMobile) {
					// Add a slight delay to ensure ReCAPTCHA is fully loaded
					setTimeout(() => {
						const recaptchaIframe = document.querySelector('iframe[title="reCAPTCHA"]');
						if (recaptchaIframe) {
							// Ensure iframe is interactive
							(recaptchaIframe as HTMLElement).style.position = "relative";
							(recaptchaIframe as HTMLElement).style.zIndex = "999";
							(recaptchaIframe as HTMLElement).style.touchAction = "manipulation";
						}
					}, 1000);
				}
			}
		};

		handleRecaptchaOnMobile();
		window.addEventListener("resize", handleRecaptchaOnMobile);

		return () => {
			window.removeEventListener("resize", handleRecaptchaOnMobile);
		};
	}, []);

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setErrorMessage("");
		setSuccessMessage("");
		setIsSubmitting(true);

		// Form validation
		if (!email) {
			setErrorMessage("Please enter your email address.");
			setIsSubmitting(false);
			return;
		}

		if (!isChecked) {
			setErrorMessage("Please agree to receive email updates.");
			setIsSubmitting(false);
			return;
		}

		// Get reCAPTCHA value
		const recaptchaValue = recaptchaRef.current?.getValue();

		if (!recaptchaValue) {
			setErrorMessage("Please verify you're human by completing the CAPTCHA.");
			setIsSubmitting(false);
			return;
		}

		try {
			// We don't need to send the actual recaptcha token to MailerLite
			// Just check it locally and then proceed with subscription
			const response = await fetch("https://connect.mailerlite.com/api/subscribers", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json",
					Authorization: `Bearer ${process.env.NEXT_PUBLIC_MAILERLITE_TOKEN}`
				},
				body: JSON.stringify({
					email: email,
					groups: [process.env.NEXT_PUBLIC_MAILERLITE_GROUP_ID] // Fixed array syntax
				})
			});

			const data = await response.json();

			if (response.ok) {
				setSuccessMessage(
					"Almost done! We've sent a confirmation email. Please click the link to complete your subscription."
				);
				setEmail("");
				setIsChecked(false);
				recaptchaRef.current?.reset();
				setFormSubmitted(true); // Set this to true on successful submission
			} else {
				if (data.message) {
					setErrorMessage(data.message);
				} else {
					setErrorMessage("Something went wrong. Please try again later.");
				}
			}
		} catch {
			setErrorMessage("Failed to connect to subscription service. Please try again later.");
		}

		setIsSubmitting(false);
	};

	return (
		<>
			<Head>
				<title>jobba.help</title>
				<meta content="width=device-width, initial-scale=1.0" name="viewport" />
				<link href="/favicon-96x96.png" rel="icon" sizes="96x96" type="image/png" />
				<link href="/apple-touch-icon.png" rel="apple-touch-icon" sizes="180x180" />
				<meta content="jobba.help" name="apple-mobile-web-app-title" />
				<link href="/static/site.webmanifest" rel="manifest" />
			</Head>

			{/* Add mobile-friendly ReCAPTCHA styles */}
			<style global jsx>{`
				/* ReCAPTCHA Mobile Fixes */
				.recaptcha-container {
					display: flex;
					justify-content: center;
					align-items: center;
					margin-bottom: 20px;
					width: 100%;
					position: relative;
					/* Remove overflow: hidden which might be clipping the checkbox */
				}

				/* Critical fix for mobile clickability */
				.recaptcha-container > div {
					position: relative;
					z-index: 1;
					/* Make sure inner container is centered */
					margin: 0 auto;
				}

				/* Ensure iframe is clickable */
				.recaptcha-container iframe {
					position: relative;
					z-index: 2;
					touch-action: manipulation;
				}

				/* Handle very small screens */
				@media (max-width: 400px) {
					.recaptcha-container > div {
						/* Center the component better */
						transform: scale(0.9);
						transform-origin: center center;
						margin: 0 auto;
					}

					/* Add more space around captcha to ensure nothing gets cut off */
					.recaptcha-container {
						padding: 10px 0;
						min-height: 78px; /* Match height of scaled captcha */
					}
				}

				/* Target the specific iframe that contains the checkbox */
				.recaptcha-container iframe[title="reCAPTCHA"] {
					display: block;
					margin: 0 auto;
				}
			`}</style>

			<main className="max-w-2xl mx-auto p-6 shadow-md rounded-lg bg-white dark:bg-gray-800">
				<div className="mb-8 p-5 border border-blue-100 dark:border-blue-900 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
					<h2 className="text-2xl font-bold text-blue-800 dark:text-blue-300 mb-4">
						<span className="inline-block mr-2">📊</span>
						jobba.help
					</h2>

					<p className="text-gray-700 dark:text-gray-300 mb-4">
						An open-source job application tracker that works automatically with your email.
					</p>

					<div className="space-y-3">
						{/* Feature 1 */}
						<div className="flex items-start">
							<div className="flex-shrink-0 mt-1">
								<svg
									className="h-5 w-5 text-blue-600 dark:text-blue-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
									/>
								</svg>
							</div>
							<p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
								<span className="font-medium text-gray-900 dark:text-white">Automatic tracking</span> —
								Connects to your email inbox to find job applications
							</p>
						</div>

						{/* Feature 2 */}
						<div className="flex items-start">
							<div className="flex-shrink-0 mt-1">
								<svg
									className="h-5 w-5 text-blue-600 dark:text-blue-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
									/>
								</svg>
							</div>
							<p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
								<span className="font-medium text-gray-900 dark:text-white">No manual data entry</span>{" "}
								— Simply log in and see your application history
							</p>
						</div>
					</div>
				</div>
				{/* MailerLite Signup Form */}
				<div className="mb-10 p-6 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
					<h2 className="text-2xl font-bold mb-3 text-gray-900 dark:text-white">Join the Waitlist</h2>
					<p className="mb-6 text-gray-600 dark:text-gray-300">
						When jobba.help launches outside of beta, you'll be the first to know!
					</p>

					{errorMessage && (
						<div className="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300">
							{errorMessage}
						</div>
					)}

					{successMessage && (
						<div className="mb-4 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-md text-green-700 dark:text-green-300">
							{successMessage}
						</div>
					)}

					{!formSubmitted ? (
						<form onSubmit={handleSubmit}>
							<div className="mb-4">
								<label
									className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
									htmlFor="email"
								>
									Email address
								</label>
								<input
									required
									className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
									id="email"
									placeholder="you@example.com"
									type="email"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
								/>
							</div>

							<div className="mb-4">
								<label className="inline-flex items-center">
									<input
										checked={isChecked}
										className="rounded border-gray-300 dark:border-gray-600 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 dark:bg-gray-700"
										type="checkbox"
										onChange={(e) => setIsChecked(e.target.checked)}
									/>
									<span className="ml-2 text-sm text-gray-600 dark:text-gray-300">
										Opt in to receive updates by email about jobba.help
									</span>
								</label>
							</div>

							<div className="mb-6">
								<ReCAPTCHA
									ref={recaptchaRef}
									className="recaptcha-container"
									sitekey={
										process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ||
										"6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
									}
									size="normal" // Changed from compact for better clickability
									theme={isDarkMode ? "dark" : "light"}
								/>
							</div>

							<button
								className="w-full px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800 rounded-md shadow transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70"
								disabled={isSubmitting}
								type="submit"
							>
								{isSubmitting ? "Subscribing..." : "Subscribe"}
							</button>
						</form>
					) : null}
				</div>

				<h2 className="text-2xl font-bold mt-6 mb-4 text-gray-900 dark:text-white">Resources</h2>

				<div className="space-y-4">
					{/* Discord Resource Card */}
					<a
						className="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200 bg-white dark:bg-gray-800 dark:border-gray-700"
						href="https://discord.gg/5tTT6WVQyw"
					>
						<div className="flex items-center">
							<div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-900 p-3 rounded-lg">
								<svg
									className="h-6 w-6 text-indigo-600 dark:text-indigo-300"
									fill="currentColor"
									viewBox="0 0 24 24"
								>
									<path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 0 0-.079.036c-.21.39-.444.885-.608 1.28a18.566 18.566 0 0 0-5.487 0 12.217 12.217 0 0 0-.617-1.28.077.077 0 0 0-.079-.036c-1.714.29-3.354.8-4.885 1.491a.07.07 0 0 0-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 0 0 .031.055 20.03 20.03 0 0 0 5.993 2.98.078.078 0 0 0 .084-.026 13.83 13.83 0 0 0 1.226-1.963.074.074 0 0 0-.041-.104 13.201 13.201 0 0 1-1.872-.878.075.075 0 0 1-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 0 1 .078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 0 1 .078.009c.12.098.246.195.372.288a.075.075 0 0 1-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 0 0-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 0 0 .084.028 19.963 19.963 0 0 0 6.002-2.981.076.076 0 0 0 .032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 0 0-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z" />
								</svg>
							</div>
							<div className="ml-4">
								<h3 className="text-lg font-medium text-gray-900 dark:text-white">
									jobba.help Community on Discord
								</h3>
								<p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
									Share feature requests with the developers.
								</p>
							</div>
						</div>
					</a>

					{/* Never Search Alone Resource Card */}
					<a
						className="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200 bg-white dark:bg-gray-800 dark:border-gray-700"
						href="https://www.phyl.org/"
					>
						<div className="flex items-center">
							<div className="flex-shrink-0 bg-emerald-100 dark:bg-emerald-900 p-3 rounded-lg">
								<svg
									className="h-6 w-6 text-emerald-600 dark:text-emerald-300"
									fill="none"
									stroke="currentColor"
									strokeWidth="2"
									viewBox="0 0 24 24"
								>
									<path
										d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
										strokeLinecap="round"
										strokeLinejoin="round"
									/>
								</svg>
							</div>
							<div className="ml-4">
								<h3 className="text-lg font-medium text-gray-900 dark:text-white">
									Never Search Alone - phyl.org
								</h3>
								<p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
									Join a free peer support group with a thriving online community of job seekers.
								</p>
							</div>
						</div>
					</a>
				</div>
			</main>
		</>
	);
}
