"use client";

import { FC } from "react";
import { VisuallyHidden } from "@react-aria/visually-hidden";
import { SwitchProps, useSwitch } from "@heroui/react";
import { useTheme } from "next-themes";
import { useIsSSR } from "@react-aria/ssr";
import clsx from "clsx";

import { SunFilledIcon, MoonFilledIcon } from "@/components/icons";

export interface ThemeSwitchProps {
	className?: string;
	classNames?: SwitchProps["classNames"];
	children?: React.ReactNode;
}

export const ThemeSwitch: FC<ThemeSwitchProps> = ({ className, classNames, children }) => {
	const { theme, setTheme } = useTheme();
	const isSSR = useIsSSR();

	const onChange = () => {
		if (theme === "light") {
			setTheme("dark");
		} else {
			setTheme("light");
		}
	};

	const { Component, slots, isSelected, getBaseProps, getInputProps, getWrapperProps } = useSwitch({
		isSelected: theme === "light" || isSSR,
		"aria-label": `Switch to ${theme === "light" || isSSR ? "dark" : "light"} mode`,
		onChange
	});

	return (
		<Component
			{...getBaseProps({
				className: clsx("px-px transition-opacity hover:opacity-80 cursor-pointer", className, classNames?.base)
			})}
		>
			<VisuallyHidden>
				<input {...getInputProps()} />
			</VisuallyHidden>
			<div
				{...getWrapperProps()}
				className={slots.wrapper({
					class: clsx(
						[
							"w-auto h-auto",
							"bg-transparent",
							"rounded-lg",
							"flex items-center justify-center gap-2", // Added gap for spacing
							"group-data-[selected=true]:bg-transparent",
							"!text-default-500",
							"pt-px",
							"px-0",
							"mx-0"
						],
						classNames?.wrapper
					)
				})}
			>
				<div data-testid="theme-switch-button">
					{!isSelected || isSSR ? <SunFilledIcon size={22} /> : <MoonFilledIcon size={22} />}
					{children && <span className="text-default-600">{children}</span>}
				</div>
			</div>
		</Component>
	);
};
