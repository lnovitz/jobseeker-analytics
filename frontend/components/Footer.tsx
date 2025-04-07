import { EmailIcon, ExternalLinkIcon } from "@/components/icons";

const Footer = () => {
	return (
		<footer className="border-t py-12 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
			<div className="container mx-auto px-4">
				<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
					<div>
						<h3 className="text-lg font-semibold mb-4">About jobba.help</h3>
						<p className="text-default-500 mb-4">
							Treat job hunting like a sales funnel – track response rates, follow-ups, and conversions,
							just like a business. Be data-driven.
						</p>
						<p className="text-sm text-default-500">Currently in beta (100 user testing limit)</p>
					</div>

					<div>
						<h3 className="text-lg font-semibold mb-4">Tech Stack</h3>
						<ul className="space-y-2 text-default-500">
							<li>Frontend: Next.js, TypeScript</li>
							<li>Backend: FastAPI, Python</li>
							<li>Database: PostgreSQL</li>
							<li>Integrations: Gmail API, Posthog</li>
						</ul>
					</div>

					<div>
						<h3 className="text-lg font-semibold mb-4">Connect With Us</h3>
						<div className="space-y-4">
							<a
								className="flex items-center gap-2 text-sm text-default-500 hover:text-foreground transition-colors"
								href="https://discord.gg/5tTT6WVQyw"
								rel="noopener noreferrer"
								target="_blank"
							>
								<ExternalLinkIcon size={16} />
								Join our Discord
							</a>
							<a
								className="flex items-center gap-2 text-sm text-default-500 hover:text-foreground transition-colors"
								href="mailto:help@jobba.help"
							>
								<EmailIcon size={16} />
								help@jobba.help
							</a>
							<a
								className="flex items-center gap-2 text-sm text-default-500 hover:text-foreground transition-colors"
								href="mailto:security@jobba.help"
							>
								<EmailIcon size={16} />
								security@jobba.help
							</a>
						</div>
					</div>
				</div>

				<div className="mt-12 pt-6 border-t text-center text-sm text-default-500">
					<p>
						jobba.help is open source - future developers can always fork this project and continue the
						work.
					</p>
					<p className="mt-2">© {new Date().getFullYear()} jobba.help</p>
				</div>
			</div>
		</footer>
	);
};

export default Footer;
