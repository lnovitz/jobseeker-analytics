interface GoogleApiClientConfig {
	apiKey?: string;
	clientId?: string;
	discoveryDocs?: string[];
	scope?: string;
}

interface GmailFilterResource {
	action?: {
		addLabelIds?: string[];
		removeLabelIds?: string[];
		forward?: string;
	};
	criteria?: {
		from?: string;
		to?: string;
		subject?: string;
		hasAttachment?: boolean;
		excludeChats?: boolean;
		negatedQuery?: string;
		query?: string;
	};
}

interface GmailFilterResponse {
	id: string;
	criteria: Record<string, unknown>;
	action: Record<string, unknown>;
}

interface GoogleAuthUser {
	getBasicProfile(): {
		getName(): string;
		getEmail(): string;
		getId(): string;
	};
	getAuthResponse(): {
		id_token: string;
		access_token: string;
	};
}

interface Window {
	gapi: {
		load: (api: string, callback: () => void) => void;
		client: {
			init: (config: GoogleApiClientConfig) => Promise<void>;
			gmail: {
				users: {
					settings: {
						filters: {
							create: (params: {
								userId: string;
								resource: GmailFilterResource;
							}) => Promise<GmailFilterResponse>;
						};
					};
				};
			};
		};
		auth2: {
			getAuthInstance: () => {
				signIn: () => Promise<GoogleAuthUser>;
			};
		};
	};
}
