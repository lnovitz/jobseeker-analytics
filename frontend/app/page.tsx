"use client";
import Head from "next/head";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Button } from "@heroui/react";

import { GoogleIcon } from "@/components/icons";

const GoogleLogin = () => {
	const router = useRouter();

	const handleGoogleLogin = () => {
		router.push("http://localhost:8000/login");
	};

	return (
		<Button
			bg-default-100
			className="text-sm font-normal text-default-600"
			startContent={<GoogleIcon className="text-danger" />}
			variant="flat"
			onPress={handleGoogleLogin} // Callback prop should be last
		>
			Login with Google
		</Button>
	);
};

export default function Home() {
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

			<main className="max-w-2xl mx-auto p-6 shadow-md rounded-lg">
				<h2 className="text-2xl font-bold">Did you email us yet? No?</h2>
				<p>
					To beta test,{" "}
					<a
						className="text-blue-600 hover:underline"
						href="mailto:help@jobba.help?subject=JobbaHelp%20Free%20Trial&body=my%20google%20gmail%20address%20is"
					>
						send us an email
					</a>
					.
				</p>
				<ol className="list-decimal ml-6">
					<li>Mention how you heard about the app (which community, friend’s name).</li>
					<li>We’ll respond as soon as possible to give you access.</li>
				</ol>

				<h2 className="text-2xl font-bold mt-6">Did you get a confirmation email? Ready to start?</h2>
				<div className="mt-4 flex">
					<GoogleLogin />
				</div>

				<div className="flex justify-center mt-6">
					<iframe
						allowFullScreen
						className="rounded-lg shadow-md"
						height="315"
						src="https://www.youtube.com/embed/-cOKR4JtceY"
						title="YouTube video player"
						width="560"
					/>
				</div>

				<h2 className="text-2xl font-bold mt-6">What&apos;s this about?</h2>
				<p className="text-center text-3xl">↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓</p>

				<h2 className="text-2xl font-bold mt-6">
					&ldquo;What&apos;s special about another job tracker spreadsheet?&rdquo;
				</h2>
				<p>
					The spreadsheet is <strong>automagically updated</strong>&mdash;you don’t need to update it
					manually.
				</p>
				<p>Log in with Google, and bam! The spreadsheet is generated for you.</p>

				<h2 className="text-2xl font-bold mt-6">&ldquo;Are you reading my emails?!&rdquo;</h2>
				<p>Nope! The app simply fetches relevant job application emails and logs them.</p>

				<h2 className="text-2xl font-bold mt-6">How does it work?</h2>
				<p>
					When you log in with Google, the app gets a temporary access token for fetching job-related emails.
				</p>

				<pre className="p-4 rounded-lg text-sm mt-4 whitespace-pre-wrap break-words">
					&apos;(subject:&quot;thank&quot; AND from:&quot;no-reply@ashbyhq.com&quot;) OR{"\n"}
					&apos;(subject:&quot;thank&quot; AND from:&quot;careers@&quot;) OR{"\n"}
					&apos;subject:&quot;application received&quot; OR{"\n"}
					&apos;subject:&quot;we received your application&quot; OR{"\n"}
					&apos;subject:&quot;thank you for your application&quot;
				</pre>

				<h2 className="text-2xl font-bold mt-4">Your data will look something like this:</h2>
				<div className="mt-6 flex justify-center">
					<Image
						alt="Spreadsheet Example"
						className="rounded-lg shadow-md"
						height={400}
						src="/excel_ss.png"
						width={700}
					/>
				</div>

				<h2 className="text-2xl font-bold mt-6">Did you email us yet?</h2>
				<p>
					To beta test,{" "}
					<a
						className="text-blue-600 hover:underline"
						href="mailto:help@jobba.help?subject=JobbaHelp%20Free%20Trial&body=my%20google%20gmail%20address%20is"
					>
						send us an email
					</a>
					.
				</p>
				<h2 className="text-2xl font-bold mt-6">Resources</h2>
				<ul>
					<li>
						<a href="https://discord.gg/5tTT6WVQyw">jobba.help Community on Discord</a>
					</li>
					<li>
						<a href="https://www.phyl.org/">
							Never Search Alone - phyl.org - Free Support Group for Job Seekers
						</a>
					</li>
				</ul>
			</main>
		</>
	);
}
