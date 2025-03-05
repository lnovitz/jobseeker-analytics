"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const Playground = () => {
	const router = useRouter();

	useEffect(() => {
		if (process.env.NEXT_PUBLIC_ENV_TYPE !== "dev") {
			router.push("/");
		}
	}, [router]);

	if (process.env.NEXT_PUBLIC_ENV_TYPE !== "dev") {
		return null;
	}

	const handleInsert = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const name = (event.target as any).name.value;
		const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/insert`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({ name })
		});
		const result = await response.json();
		alert(result.message);
	};

	const handleDelete = async () => {
		const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/delete`, {
			method: "DELETE"
		});
		const result = await response.json();
		alert(result.message);
	};

	return (
		<div>
			<h1>Database Test (Development Only)</h1>
			<p>This page is for developers to try out the database and get familiar with how Docker works.</p>
			<form onSubmit={handleInsert}>
				<label htmlFor="name">Name:</label>
				<input required id="name" name="name" type="text" />
				<button type="submit">Insert Data</button>
			</form>
			<button onClick={handleDelete}>Delete All Data</button>
		</div>
	);
};

export default Playground;
