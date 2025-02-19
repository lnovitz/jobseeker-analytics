export default function SuccessPage() {
	const apiUrl = process.env.NEXT_PUBLIC_API_URL!;
	return (
		<div className="flex flex-col items-center justify-center text-center pt-64">
			<h1 className="text-3xl font-bold text-green-500">Success! Your file is ready.</h1>
			<p className="pt-8">Click the button below to download your file.</p>
			<a
				download
				className="mt-6 px-6 py-3 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 transition"
				href={`${apiUrl}/download-file`}
			>
				Download Job Application Data
			</a>
		</div>
	);
}
