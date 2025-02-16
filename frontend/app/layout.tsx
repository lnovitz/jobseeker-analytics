import "@/styles/globals.css";
import { Metadata, Viewport } from "next";
import Image from "next/image";
import clsx from "clsx";

import { Providers } from "./providers";

import { siteConfig } from "@/config/site";
import { fontSans } from "@/config/fonts";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
	title: {
		default: siteConfig.name,
		template: `%s - ${siteConfig.name}`
	},
	description: siteConfig.description,
	icons: {
		icon: "/favicon.ico"
	}
};

export const viewport: Viewport = {
	themeColor: [
		{ media: "(prefers-color-scheme: light)", color: "white" },
		{ media: "(prefers-color-scheme: dark)", color: "black" }
	]
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html suppressHydrationWarning lang="en">
			<head />
			<body className={clsx("min-h-screen bg-background font-sans antialiased", fontSans.variable)}>
				<Providers themeProps={{ attribute: "class", defaultTheme: "dark" }}>
					<div className="relative flex h-screen flex-col">
						<Navbar />
						<main className="container mx-auto flex-grow max-w-7xl px-6 pt-16">{children}</main>
						<footer className="flex w-full flex-col items-center py-3">
							<div className="flex h-[5rem] w-[10rem] items-center justify-center overflow-hidden rounded-lg">
								<Image
									alt="jobba.help logo"
									className="h-full w-full object-cover"
									height={80}
									src="/logo.png"
									width={160}
								/>
							</div>
							<p className="mt-2 text-center">&copy; 2025 Lianna Novitz</p>
						</footer>
					</div>
				</Providers>
			</body>
		</html>
	);
}
