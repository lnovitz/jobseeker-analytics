"use client";

import { Navbar as HeroUINavbar, NavbarContent, NavbarMenuToggle, NavbarBrand, NavbarItem } from "@heroui/react";
import { Button, Link } from "@heroui/react";
import { useRouter } from "next/navigation";
import NextLink from "next/link";

import { siteConfig } from "@/config/site";
import { ThemeSwitch } from "@/components/theme-switch";
import { GithubIcon, HeartFilledIcon, GoogleIcon } from "@/components/icons";
import { usePathname } from "next/navigation";

export const Navbar = () => {
	const pathname = usePathname();
	const router = useRouter();

	const handleGoogleLogin = () => {
		router.push("http://localhost:8000/login"); // Update with your FastAPI server URL
	};

	const handleGoogleLogout = async () => {
		router.push("http://localhost:8000/logout");
	  };

	return (
		<HeroUINavbar maxWidth="xl" position="sticky">
			<NavbarContent className="basis-1/5 sm:basis-full" justify="start">
				<NavbarBrand as="li" className="gap-3 max-w-fit">
					<NextLink className="flex justify-start items-center gap-1" href="/">
						<img src="favicon.svg" alt="Jobba Logo" className="h-20 w-20 mt-8" />
					</NextLink>
				</NavbarBrand>
			</NavbarContent>

			<NavbarContent className="hidden sm:flex basis-1/5 sm:basis-full" justify="end">
				<NavbarItem className="hidden sm:flex gap-2">
					<Link isExternal aria-label="Github" href={siteConfig.links.github}>
						<GithubIcon className="text-default-500" />
					</Link>
					<ThemeSwitch />
				</NavbarItem>
				<NavbarItem className="hidden md:flex">
					<Button
						isExternal
						as={Link}
						className="text-sm font-normal text-default-600 bg-default-100"
						href={siteConfig.links.sponsor}
						startContent={<HeartFilledIcon className="text-danger" />}
						variant="flat"
					>
						Sponsor
					</Button>
				</NavbarItem>
			</NavbarContent>

			<NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
				<Link isExternal aria-label="Github" href={siteConfig.links.github}>
					<GithubIcon className="text-default-500" />
				</Link>
				<ThemeSwitch />
				<NavbarMenuToggle />
			</NavbarContent>
			
			{pathname === "/" && (
				<NavbarItem className="hidden md:flex">
					<Button
						className="text-sm font-normal text-default-600 bg-default-100"
						startContent={<GoogleIcon className="text-danger" />}
						variant="flat"
						onClick={handleGoogleLogin}
					>
						Login with Google
					</Button>
				</NavbarItem>
			)}
			
			{/* Add for processing page too */}
			{pathname === "/success" && (
			<NavbarItem className="hidden md:flex">
					<Button
						className="text-sm font-normal text-default-600 bg-default-100"
						startContent={<GoogleIcon className="text-danger" />}
						variant="flat"
						onClick={handleGoogleLogout}
					>
						Logout
					</Button>
				</NavbarItem>
			)}
		</HeroUINavbar>
	);
};
