"use client";

import type React from "react";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { ArrowRight, BarChart2, CheckCircle, Clock, Mail, Target, Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Homepage() {
	const [email, setEmail] = useState("");

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		// Handle form submission
		console.log("Email submitted:", email);
		setEmail("");
	};

	return (
		<div className="flex min-h-screen flex-col">
			<header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
				<div className="container flex h-16 items-center justify-between">
					<div className="flex items-center gap-2">
						<Target className="h-6 w-6 text-primary" />
						<span className="text-xl font-bold">jobba.help</span>
					</div>
					<nav className="hidden md:flex gap-6">
						<Link className="text-sm font-medium hover:underline underline-offset-4" href="#features">
							Features
						</Link>
						<Link className="text-sm font-medium hover:underline underline-offset-4" href="#how-it-works">
							How It Works
						</Link>
						<Link className="text-sm font-medium hover:underline underline-offset-4" href="#pricing">
							Pricing
						</Link>
					</nav>
					<div className="flex items-center gap-4">
						<Link className="text-sm font-medium hover:underline underline-offset-4" href="/login">
							Log in
						</Link>
						<Button asChild>
							<Link href="/signup">Get Started</Link>
						</Button>
					</div>
				</div>
			</header>
			<main className="flex-1">
				{/* Hero Section */}
				<section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-b from-background to-muted">
					<div className="container px-4 md:px-6">
						<div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
							<div className="flex flex-col justify-center space-y-4">
								<div className="inline-block rounded-lg bg-primary/10 px-3 py-1 text-sm text-primary">
									Job hunting, reimagined
								</div>
								<h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
									Treat job hunting like a sales funnel
								</h1>
								<p className="max-w-[600px] text-muted-foreground md:text-xl">
									Track response rates, follow-ups, and conversions, just like a business. The only
									difference? You're the product.
								</p>
								<p className="max-w-[600px] text-muted-foreground md:text-xl">
									You deserve transparency and enterprise level analytics for the most important
									product in this job market - you.
								</p>
								<div className="flex flex-col gap-2 min-[400px]:flex-row">
									<Button asChild size="lg">
										<Link href="/signup">
											Start tracking for free <ArrowRight className="ml-2 h-4 w-4" />
										</Link>
									</Button>
									<Button asChild size="lg" variant="outline">
										<Link href="#how-it-works">See how it works</Link>
									</Button>
								</div>
							</div>
							<div className="flex items-center justify-center">
								<Image
									alt="Dashboard preview"
									className="rounded-lg object-cover shadow-xl"
									height={550}
									src="/placeholder.svg?height=550&width=450"
									width={450}
								/>
							</div>
						</div>
					</div>
				</section>

				{/* Problem Statement Section */}
				<section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
									The job search is broken
								</h2>
								<p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
									In a world where companies rely on data-driven insights for hiring, job seekers are
									left in the dark, forced to manually track their own progress with no real analytics
									on their job search performance. The labor of applying for jobs—researching,
									networking, following up—is unpaid, unseen, and unoptimized.
								</p>
							</div>
						</div>
						<div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12 mt-12">
							<Card>
								<CardHeader className="pb-2">
									<Mail className="h-6 w-6 text-primary mb-2" />
									<CardTitle>No responses</CardTitle>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Applications disappear into the void with no feedback or response from
										employers.
									</p>
								</CardContent>
							</Card>
							<Card>
								<CardHeader className="pb-2">
									<Clock className="h-6 w-6 text-primary mb-2" />
									<CardTitle>Wasted time</CardTitle>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Hours spent researching, networking, and following up with no way to measure
										effectiveness.
									</p>
								</CardContent>
							</Card>
							<Card>
								<CardHeader className="pb-2">
									<BarChart2 className="h-6 w-6 text-primary mb-2" />
									<CardTitle>No analytics</CardTitle>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Job seekers have no real analytics on their search performance or how to
										improve.
									</p>
								</CardContent>
							</Card>
						</div>
					</div>
				</section>

				{/* Features Section */}
				<section className="w-full py-12 md:py-24 lg:py-32" id="features">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<div className="inline-block rounded-lg bg-primary/10 px-3 py-1 text-sm text-primary">
									Features
								</div>
								<h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
									Your job search, optimized
								</h2>
								<p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
									We understand how frustrating it is to apply and not hear back. That's why we built
									jobba.help.
								</p>
							</div>
						</div>
						<Tabs className="mt-12" defaultValue="track">
							<TabsList className="grid w-full grid-cols-3">
								<TabsTrigger value="track">Track</TabsTrigger>
								<TabsTrigger value="analyze">Analyze</TabsTrigger>
								<TabsTrigger value="optimize">Optimize</TabsTrigger>
							</TabsList>
							<TabsContent className="mt-6" value="track">
								<div className="grid gap-6 lg:grid-cols-[1fr_500px] lg:gap-12">
									<div className="flex flex-col justify-center space-y-4">
										<h3 className="text-2xl font-bold">Track every application</h3>
										<ul className="grid gap-3">
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Application Pipeline</p>
													<p className="text-sm text-muted-foreground">
														Visualize your job search as a sales funnel with stages from
														application to offer.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Follow-up Reminders</p>
													<p className="text-sm text-muted-foreground">
														Never miss a follow-up with automated reminders and email
														templates.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Document Management</p>
													<p className="text-sm text-muted-foreground">
														Store resumes, cover letters, and company research in one place.
													</p>
												</div>
											</li>
										</ul>
									</div>
									<div className="flex items-center justify-center">
										<Image
											alt="Application tracking dashboard"
											className="rounded-lg object-cover shadow-xl"
											height={400}
											src="/placeholder.svg?height=400&width=500"
											width={500}
										/>
									</div>
								</div>
							</TabsContent>
							<TabsContent className="mt-6" value="analyze">
								<div className="grid gap-6 lg:grid-cols-[1fr_500px] lg:gap-12">
									<div className="flex flex-col justify-center space-y-4">
										<h3 className="text-2xl font-bold">Analyze your performance</h3>
										<ul className="grid gap-3">
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Response Rate Analytics</p>
													<p className="text-sm text-muted-foreground">
														See which job sources, resume versions, and application
														strategies get the best results.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Conversion Insights</p>
													<p className="text-sm text-muted-foreground">
														Track your conversion rates from application to interview to
														offer.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Industry Benchmarks</p>
													<p className="text-sm text-muted-foreground">
														Compare your metrics to industry averages and see where you
														stand.
													</p>
												</div>
											</li>
										</ul>
									</div>
									<div className="flex items-center justify-center">
										<Image
											alt="Analytics dashboard"
											className="rounded-lg object-cover shadow-xl"
											height={400}
											src="/placeholder.svg?height=400&width=500"
											width={500}
										/>
									</div>
								</div>
							</TabsContent>
							<TabsContent className="mt-6" value="optimize">
								<div className="grid gap-6 lg:grid-cols-[1fr_500px] lg:gap-12">
									<div className="flex flex-col justify-center space-y-4">
										<h3 className="text-2xl font-bold">Optimize your strategy</h3>
										<ul className="grid gap-3">
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">AI-Powered Recommendations</p>
													<p className="text-sm text-muted-foreground">
														Get personalized suggestions to improve your application success
														rate.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">A/B Testing</p>
													<p className="text-sm text-muted-foreground">
														Test different resume versions and cover letter approaches to
														see what works best.
													</p>
												</div>
											</li>
											<li className="flex items-start gap-2">
												<CheckCircle className="h-5 w-5 text-primary mt-0.5" />
												<div>
													<p className="font-medium">Networking Opportunities</p>
													<p className="text-sm text-muted-foreground">
														Identify and prioritize networking connections that can help you
														get your foot in the door.
													</p>
												</div>
											</li>
										</ul>
									</div>
									<div className="flex items-center justify-center">
										<Image
											alt="Optimization dashboard"
											className="rounded-lg object-cover shadow-xl"
											height={400}
											src="/placeholder.svg?height=400&width=500"
											width={500}
										/>
									</div>
								</div>
							</TabsContent>
						</Tabs>
					</div>
				</section>

				{/* How It Works Section */}
				<section className="w-full py-12 md:py-24 lg:py-32 bg-muted" id="how-it-works">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<div className="inline-block rounded-lg bg-primary/10 px-3 py-1 text-sm text-primary">
									How It Works
								</div>
								<h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
									Simple, yet powerful
								</h2>
								<p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
									Get started in minutes and take control of your job search.
								</p>
							</div>
						</div>
						<div className="mx-auto grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-3 lg:gap-12 mt-12">
							<div className="flex flex-col items-center space-y-2 text-center">
								<div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg font-bold text-primary-foreground">
									1
								</div>
								<h3 className="text-xl font-bold">Track applications</h3>
								<p className="text-sm text-muted-foreground">
									Log your job applications, interviews, and follow-ups in one centralized dashboard.
								</p>
							</div>
							<div className="flex flex-col items-center space-y-2 text-center">
								<div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg font-bold text-primary-foreground">
									2
								</div>
								<h3 className="text-xl font-bold">Analyze your data</h3>
								<p className="text-sm text-muted-foreground">
									Get insights into your application success rates and identify areas for improvement.
								</p>
							</div>
							<div className="flex flex-col items-center space-y-2 text-center">
								<div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg font-bold text-primary-foreground">
									3
								</div>
								<h3 className="text-xl font-bold">Optimize & succeed</h3>
								<p className="text-sm text-muted-foreground">
									Implement data-driven strategies to improve your chances of landing your dream job.
								</p>
							</div>
						</div>
					</div>
				</section>

				{/* Testimonials Section */}
				<section className="w-full py-12 md:py-24 lg:py-32">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<div className="inline-block rounded-lg bg-primary/10 px-3 py-1 text-sm text-primary">
									Testimonials
								</div>
								<h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Success stories</h2>
								<p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
									See how job seekers like you are finding success with jobba.help.
								</p>
							</div>
						</div>
						<div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-1 lg:gap-12 mt-12 place-items-center">
							<Card>
								<CardContent className="p-6">
									<div className="flex items-start gap-4">
										<div className="rounded-full bg-primary/10 p-2">
											<Users className="h-6 w-6 text-primary" />
										</div>
										<div>
											<p className="text-sm leading-relaxed text-muted-foreground mb-4">
												"I use it! It's extremely simple to use, and keeps track of my
												applications seamlessly. Thank you for building an awesome product!"
											</p>
											<p className="font-semibold">
												<a href="https://www.linkedin.com/in/vishwanshi-joshi/" target="_blank">
													Vishwanshi Joshi
												</a>
											</p>
											<p className="text-sm text-muted-foreground">Product Manager</p>
										</div>
									</div>
								</CardContent>
							</Card>
						</div>
					</div>
				</section>

				{/* Pricing Section */}
				<section className="w-full py-12 md:py-24 lg:py-32 bg-muted" id="pricing">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<div className="inline-block rounded-lg bg-primary/10 px-3 py-1 text-sm text-primary">
									Pricing
								</div>
								<h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
									Simple, transparent pricing
								</h2>
								<p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
									Start for free, upgrade when you need more features.
								</p>
							</div>
						</div>
						<div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:gap-12 mt-12">
							<Card className="border-2 border-muted">
								<CardHeader>
									<CardTitle>Free</CardTitle>
									<CardDescription>Forever</CardDescription>
									<div className="mt-4 flex items-baseline text-5xl font-bold">
										$0
										<span className="ml-1 text-lg font-medium text-muted-foreground">/month</span>
									</div>
								</CardHeader>
								<CardContent>
									<ul className="grid gap-3">
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Track unlimited applications</span>
										</li>
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Basic analytics</span>
										</li>
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Data exports</span>
										</li>
									</ul>
									<Button asChild className="mt-6 w-full" variant="outline">
										<Link href="/signup">Get Started</Link>
									</Button>
								</CardContent>
							</Card>
							<Card className="border-2 border-primary">
								<CardHeader>
									<CardTitle>Pro</CardTitle>
									<CardDescription>Just got your severance package?</CardDescription>
									<div className="mt-4 flex items-baseline text-5xl font-bold">
										$9
										<span className="ml-1 text-lg font-medium text-muted-foreground">/month</span>
									</div>
								</CardHeader>
								<CardContent>
									<ul className="grid gap-3">
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Advanced analytics & reporting</span>
										</li>
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Resume A/B testing</span>
										</li>
										<li className="flex items-center gap-2">
											<CheckCircle className="h-4 w-4 text-primary" />
											<span className="text-sm">Industry benchmarks</span>
										</li>
									</ul>
									<Button asChild className="mt-6 w-full">
										<Link href="/signup">Start 14-day free trial</Link>
									</Button>
								</CardContent>
							</Card>
						</div>
					</div>
				</section>

				{/* CTA Section */}
				<section className="w-full py-12 md:py-24 lg:py-32 bg-primary text-primary-foreground">
					<div className="container px-4 md:px-6">
						<div className="flex flex-col items-center justify-center space-y-4 text-center">
							<div className="space-y-2">
								<h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
									Ready to take control of your job search?
								</h2>
								<p className="mx-auto max-w-[700px] md:text-xl">
									Join thousands of job seekers who are optimizing their job search with jobba.help.
								</p>
							</div>
							<div className="w-full max-w-sm space-y-2">
								<form className="flex gap-2" onSubmit={handleSubmit}>
									<input
										required
										className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-lg flex-1"
										placeholder="Enter your email"
										type="email"
										value={email}
										onChange={(e) => setEmail(e.target.value)}
									/>
									<Button type="submit" variant="secondary">
										Get Started
									</Button>
								</form>
								<p className="text-xs text-primary-foreground/80">
									Free 14-day trial. No credit card required.
								</p>
							</div>
						</div>
					</div>
				</section>
			</main>
			<footer className="w-full border-t bg-background">
				<div className="container flex flex-col gap-6 py-8 md:flex-row md:items-center md:justify-between md:py-12">
					<div className="flex items-center gap-2">
						<Target className="h-6 w-6 text-primary" />
						<span className="text-xl font-bold">jobba.help</span>
					</div>
					<nav className="flex gap-4 sm:gap-6">
						<Link className="text-xs hover:underline underline-offset-4" href="#">
							Terms of Service
						</Link>
						<Link className="text-xs hover:underline underline-offset-4" href="#">
							Privacy Policy
						</Link>
						<Link className="text-xs hover:underline underline-offset-4" href="#">
							About
						</Link>
						<Link className="text-xs hover:underline underline-offset-4" href="#">
							Contact
						</Link>
					</nav>
					<div className="text-xs text-muted-foreground">
						© {new Date().getFullYear()} jobba.help. All rights reserved.
					</div>
				</div>
			</footer>
		</div>
	);
}
