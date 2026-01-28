import * as vscode from 'vscode';
import axios from 'axios';
import { spawn, ChildProcess } from 'child_process';

let serverProcess: ChildProcess | null = null;
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    console.log('Lattice Context extension activated');

    outputChannel = vscode.window.createOutputChannel('Lattice Context');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('lattice.startContextServer', startContextServer),
        vscode.commands.registerCommand('lattice.stopContextServer', stopContextServer),
        vscode.commands.registerCommand('lattice.queryContext', queryContextForCurrentFile)
    );

    // Auto-start if configured
    const config = vscode.workspace.getConfiguration('lattice');
    if (config.get('autoStart')) {
        startContextServer();
    }

    // Register Copilot context provider
    registerCopilotContextProvider(context);
}

export function deactivate() {
    stopContextServer();
    if (outputChannel) {
        outputChannel.dispose();
    }
}

async function startContextServer() {
    if (serverProcess) {
        vscode.window.showInformationMessage('Lattice context server already running');
        return;
    }

    const config = vscode.workspace.getConfiguration('lattice');
    const port = config.get('serverPort', 8081);

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    outputChannel.appendLine(`Starting Lattice context server on port ${port}...`);

    // Start the server using the lattice CLI
    serverProcess = spawn('lattice', ['copilot', '--port', port.toString()], {
        cwd: workspaceFolder.uri.fsPath,
        shell: true
    });

    serverProcess.stdout?.on('data', (data) => {
        outputChannel.appendLine(data.toString());
    });

    serverProcess.stderr?.on('data', (data) => {
        outputChannel.appendLine(`ERROR: ${data.toString()}`);
    });

    serverProcess.on('close', (code) => {
        outputChannel.appendLine(`Server process exited with code ${code}`);
        serverProcess = null;
    });

    // Wait a bit for server to start
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check if server is running
    try {
        await axios.get(`http://localhost:${port}/health`);
        vscode.window.showInformationMessage('Lattice context server started successfully');
        outputChannel.show(true);
    } catch (error) {
        vscode.window.showErrorMessage('Failed to start Lattice context server. Check output for details.');
        outputChannel.show(true);
    }
}

function stopContextServer() {
    if (serverProcess) {
        outputChannel.appendLine('Stopping Lattice context server...');
        serverProcess.kill();
        serverProcess = null;
        vscode.window.showInformationMessage('Lattice context server stopped');
    } else {
        vscode.window.showInformationMessage('No context server running');
    }
}

async function queryContextForCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const config = vscode.workspace.getConfiguration('lattice');
    const port = config.get('serverPort', 8081);
    const maxResults = config.get('maxContextResults', 5);

    const fileName = editor.document.fileName;

    try {
        const response = await axios.post(`http://localhost:${port}/context/file`, {
            query: fileName,
            max_results: maxResults
        });

        const context = response.data.context;

        if (context) {
            // Show context in a new editor
            const doc = await vscode.workspace.openTextDocument({
                content: context,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc, {
                viewColumn: vscode.ViewColumn.Beside,
                preview: true
            });
        } else {
            vscode.window.showInformationMessage('No context found for this file');
        }
    } catch (error) {
        vscode.window.showErrorMessage('Failed to query context. Make sure server is running.');
    }
}

function registerCopilotContextProvider(context: vscode.ExtensionContext) {
    // This is a placeholder for future Copilot API integration
    // GitHub Copilot's official context API is still in development
    // For now, users can use the /context/chat endpoint manually

    const config = vscode.workspace.getConfiguration('lattice');
    const port = config.get('serverPort', 8081);

    outputChannel.appendLine(`Copilot context available at: http://localhost:${port}/context/chat`);
    outputChannel.appendLine('Use this endpoint in your Copilot Chat to get institutional knowledge');
}
