"use client";
import { useRouter } from "next/navigation";
import { addToast, Button, Card, CardHeader, Checkbox, Input } from "@heroui/react";
import { useState, useRef, useEffect } from "react";
import ReCAPTCHA from "react-google-recaptcha";

import { CheckCircleIcon, DiscordIcon2, NeverSearchAloneIcon } from "@/components/icons";

export default function Home() {
	// Form state
	const [email, setEmail] = useState("");
	const [isChecked, setIsChecked] = useState(false);
	const [errorMessage, setErrorMessage] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [formSubmitted, setFormSubmitted] = useState(false);
	const [loading, setLoading] = useState(false);
	const router = useRouter();

	// Dark mode detection
	const [isDarkMode, setIsDarkMode] = useState(false);

	// ReCAPTCHA reference
	const recaptchaRef = useRef<ReCAPTCHA>(null);

	// Handle preview
	function tryPreview() {
		setLoading(true);
		addToast({
			title: "Previewing the app...",
			description: "Simulating Google Login",
			timeout: 2000,
			color: "success",
			shouldShowTimeoutProgress: true
		});

		setTimeout(() => {
			setLoading(false);
			router.push("/preview/processing");
		}, 2000);
	}

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
							<div className="flex-shrink-0">
								<CheckCircleIcon />
							</div>
							<p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
								<span className="font-medium text-gray-900 dark:text-white">Automatic tracking</span> —
								Connects to your email inbox to find job applications
							</p>
						</div>

						{/* Feature 2 */}
						<div className="flex items-start">
							<div className="flex-shrink-0">
								<CheckCircleIcon />
							</div>
							<p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
								<span className="font-medium text-gray-900 dark:text-white">No manual data entry</span>{" "}
								— Simply log in and see your application history
							</p>
						</div>
					</div>
				</div>

				{/* Preview User Flow */}
				<div className="mb-10 p-6 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
					<h2 className="text-2xl font-bold mb-3 text-gray-900 dark:text-white">
						Want to see what the app is like?
					</h2>
					<p className="mb-4 text-gray-600 dark:text-gray-300">
						Click the button below to simulate the app using sample data
					</p>
					<Button className="w-full" color="primary" isLoading={loading} variant="ghost" onPress={tryPreview}>
						Try it out!
					</Button>
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
								<Input
									isRequired
									classNames={{ inputWrapper: "bg-default-200 dark:bg-gray-700" }}
									label="Email Address"
									placeholder="you@example.com"
									type="email"
									value={email}
									variant="faded"
									onChange={(e) => setEmail(e.target.value)}
								/>
							</div>

							<div className="mb-4">
								<label className="inline-flex items-center">
									<Checkbox
										isRequired
										checked={isChecked}
										onChange={(e) => setIsChecked(e.target.checked)}
									>
										Opt in to receive updates by email about jobba.help
									</Checkbox>
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

							<Button className="w-full" color="primary" disabled={isSubmitting} type="submit">
								{isSubmitting ? "Subscribing..." : "Subscribe"}
							</Button>
						</form>
					) : null}
				</div>
				<h2 className="text-2xl font-bold mt-6 mb-4 text-gray-900 dark:text-white">Resources</h2>

				<div className="space-y-4">
					{/* Discord Resource Card */}
					<Card
						isHoverable
						isPressable
						className="w-full p-1.5 border border-default-300 bg-white dark:bg-gray-800"
						onPress={() => (window.location.href = "https://discord.gg/5tTT6WVQyw")}
					>
						<CardHeader className="flex gap-3 w-full">
							<div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-900 p-3 rounded-lg">
								<DiscordIcon2 />
							</div>
							<div className="flex flex-col w-full text-left">
								<p className="text-lg text-left">jobba.help Community on Discord</p>
								<p className="text-small text-default-500 text-left">
									Share feature requests with the developers.
								</p>
							</div>
						</CardHeader>
					</Card>

					{/* Never Search Alone Resource Card */}
					<Card
						isHoverable
						isPressable
						className="w-full p-1.5 border border-default-300 bg-white dark:bg-gray-800"
						onPress={() => (window.location.href = "https://www.phyl.org")}
					>
						<CardHeader className="flex gap-3 w-full">
							<div className="flex-shrink-0 bg-emerald-100 dark:bg-emerald-900 p-3 rounded-lg">
								<NeverSearchAloneIcon />
							</div>
							<div className="flex flex-col w-full text-left">
								<p className="text-lg text-left">Never Search Alone - phyl.org</p>
								<p className="text-small text-default-500 text-left">
									Join a free peer support group with a thriving online community of job seekers.
								</p>
							</div>
						</CardHeader>
					</Card>
				</div>
			</main>
		</>
	);
}
