import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeConnectionTypes,
	NodeApiError,
	NodeOperationError,
} from 'n8n-workflow';

export class ComponentFinder implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Component Finder Agent',
		name: 'componentFinder',
		icon: 'file:componentFinder.svg',
		group: ['transform'],
		version: 1,
		subtitle: '={{$parameter["query"]}}',
		description: 'Runs the Lebanon Electronics Component Finder AI agent for a given component',
		defaults: {
			name: 'Component Finder Agent',
		},
		inputs: [NodeConnectionTypes.Main],
		outputs: [NodeConnectionTypes.Main],
		credentials: [
			{
				name: 'componentFinderApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Query',
				name: 'query',
				type: 'string',
				default: '',
				required: true,
				placeholder: 'e.g. LM358 op-amp',
				description: 'The electronics component to search for',
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		const credentials = await this.getCredentials('componentFinderApi');
		const baseUrl = (credentials.baseUrl as string) || 'http://host.docker.internal:8000';
		const apiKey = credentials.geminiApiKey as string;

		if (!apiKey) {
			throw new NodeOperationError(
				this.getNode(),
				'Gemini API Key is missing from the Component Finder Agent API credential.',
			);
		}

		for (let i = 0; i < items.length; i++) {
			// Query can come from a fixed value OR an expression referencing
			// a field on the incoming item, e.g. ={{$json.componentName}}
			const query = this.getNodeParameter('query', i) as string;

			try {
				const response = (await this.helpers.httpRequest({
					method: 'POST',
					url: `${baseUrl}/run-agent`,
					body: {
						message: query,
						api_key: apiKey,
					},
					json: true,
				})) as { answer: string };

				returnData.push({
					json: {
						query,
						answer: response.answer,
					},
					pairedItem: { item: i },
				});
			} catch (error) {
				throw new NodeApiError(this.getNode(), error as any, {
					message: `Component Finder Agent request failed: ${(error as Error).message}`,
					description:
						'Make sure the FastAPI service (agent_api.py) is running on your machine and reachable from Docker at the Agent Service URL set in the credential.',
				});
			}
		}

		return [returnData];
	}
}
