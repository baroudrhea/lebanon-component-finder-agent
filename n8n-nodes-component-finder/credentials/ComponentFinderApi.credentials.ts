import {
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

// This is what makes the Gemini API key satisfy the assignment's
// "store secrets in n8n's credential store, nothing hardcoded" requirement.
// It never lives in the node code or in a workflow expression -- it's
// entered once here, encrypted by n8n, and injected into the node at
// execution time.
export class ComponentFinderApi implements ICredentialType {
	name = 'componentFinderApi';

	displayName = 'Component Finder Agent API';

	documentationUrl = 'https://github.com/baroudrhea/lebanon-component-finder-agent';

	properties: INodeProperties[] = [
		{
			displayName: 'Gemini API Key',
			name: 'geminiApiKey',
			type: 'string',
			typeOptions: { password: true },
			default: '',
			required: true,
			description: 'Your Google Gemini API key. Used by the agent to call the Gemini model.',
		},
		{
			displayName: 'Agent Service URL',
			name: 'baseUrl',
			type: 'string',
			default: 'http://host.docker.internal:8000',
			description:
				'URL where the FastAPI wrapper around agent.py is running. Use host.docker.internal (not localhost) since n8n runs inside its own Docker container.',
		},
	];
}
