import pylspclient
import subprocess
import threading

# In order to run this example, you need to have python-language-server module installed.
# See more information on the project page: https://github.com/palantir/python-language-server


def configurationCallback(params):
    items = params.get("items", [])
    result = []
    for item in items:
        section = item.get("section", "")
        if section == "gopls":
            result.append({
                'annotations': {
                    'escape': True,
                    'inline': True,
                    'bounds': True,
                    'nil': True
                },
                'hoverKind': 'FullDocumentation',
                'usePlaceholders': False,
                'noSemanticNumber': False,
                'symbolMatcher': 'FastFuzzy',
                'semanticTokens': False,
                'completionBudget': '100ms',
                'experimentalPackageCacheKey': True,
                'matcher': 'Fuzzy',
                'symbolStyle': 'Dynamic',
                'templateExtensions': [],
                'buildFlags': [],
                'staticcheck': False,
                'vulncheck': 'Off',
                'linkTarget': 'pkg.go.dev',
                'allowModfileModifications': False,
                'diagnosticsDelay': '250ms',
                'noSemanticString': False,
                'experimentalPostfixCompletions': True,
                'standaloneTags': ['ignore'],
                'verboseOutput': False,
                'linksInHover': True,
                'importShortcut': 'Both',
                'hints': {},
                'local': '',
                'analyses': {},
                'allowImplicitNetworkAccess': False,
                'experimentalWatchedFileDelay': '0s',
                'directoryFilters': ['-**/node_modules'],
                'expandWorkspaceToModule': True,
                'memoryMode': 'Normal',
                'gofumpt': False,
                'env': {},
                'codelenses': {
                    'gc_details': False,
                    'upgrade_dependency': True,
                    'generate': True,
                    'tidy': True,
                    'vendor': True,
                    'regenerate_cgo': True
                },
                'experimentalWorkspaceModule': False
            })
        else:
            result.append({})
    return result


def diagnosticsCallback(params):
    # print("文件诊断: {}".format(params))
    return None


def logMessageCallback(params):
    message = params.get("message", "")
    if message:
        # print(message)
        pass


def showMessageCallback(params):
    message = params.get("message", "")
    if message:
        # print("DEBUG: {}".format(message))
        pass


class ReadPipe(threading.Thread):

    def __init__(self, pipe):
        threading.Thread.__init__(self)
        self.pipe = pipe

    def run(self):
        line = self.pipe.readline().decode('utf-8')
        while line:
            print(line)
            line = self.pipe.readline().decode('utf-8')


if __name__ == "__main__":
    gopls_cmd = ["gopls", "serve", "-mode", "stdio"]
    p = subprocess.Popen(gopls_cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    read_pipe = ReadPipe(p.stderr)
    read_pipe.start()
    json_rpc_endpoint = pylspclient.JsonRpcEndpoint(p.stdin, p.stdout)
    method_callbacks = {
        "client/registerCapability": lambda _: None,
        "workspace/configuration": configurationCallback,
    }
    notify_callbacks = {
        "window/logMessage": logMessageCallback,
        "window/showMessage": showMessageCallback,
        "textDocument/publishDiagnostics": diagnosticsCallback
    }
    # To work with socket: sock_fd = sock.makefile()
    lsp_endpoint = pylspclient.LspEndpoint(json_rpc_endpoint,
                                           method_callbacks=method_callbacks,
                                           notify_callbacks=notify_callbacks)

    lsp_client = pylspclient.LspClient(lsp_endpoint)
    capabilities = {
        'textDocument': {
            'codeAction': {
                'dynamicRegistration': True
            },
            'codeLens': {
                'dynamicRegistration': True
            },
            'colorProvider': {
                'dynamicRegistration': True
            },
            'completion': {
                'completionItem': {
                    'commitCharactersSupport': True,
                    'documentationFormat': ['markdown', 'plaintext'],
                    'snippetSupport': True
                },
                'completionItemKind': {
                    'valueSet': [
                        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                        17, 18, 19, 20, 21, 22, 23, 24, 25
                    ]
                },
                'contextSupport': True,
                'dynamicRegistration': True
            },
            'definition': {
                'dynamicRegistration': True
            },
            'documentHighlight': {
                'dynamicRegistration': True
            },
            'documentLink': {
                'dynamicRegistration': True
            },
            'documentSymbol': {
                'dynamicRegistration': True,
                'symbolKind': {
                    'valueSet': [
                        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                        17, 18, 19, 20, 21, 22, 23, 24, 25, 26
                    ]
                }
            },
            'formatting': {
                'dynamicRegistration': True
            },
            'hover': {
                'contentFormat': ['markdown', 'plaintext'],
                'dynamicRegistration': True
            },
            'implementation': {
                'dynamicRegistration': True
            },
            'onTypeFormatting': {
                'dynamicRegistration': True
            },
            'publishDiagnostics': {
                'relatedInformation': True
            },
            'rangeFormatting': {
                'dynamicRegistration': True
            },
            'references': {
                'dynamicRegistration': True
            },
            'rename': {
                'dynamicRegistration': True
            },
            'signatureHelp': {
                'dynamicRegistration': True,
                'signatureInformation': {
                    'documentationFormat': ['markdown', 'plaintext']
                }
            },
            'synchronization': {
                'didSave': True,
                'dynamicRegistration': True,
                'willSave': True,
                'willSaveWaitUntil': True
            },
            'typeDefinition': {
                'dynamicRegistration': True
            }
        },
        'workspace': {
            'applyEdit': True,
            'configuration': True,
            'didChangeConfiguration': {
                'dynamicRegistration': True
            },
            'didChangeWatchedFiles': {
                'dynamicRegistration': True
            },
            'executeCommand': {
                'dynamicRegistration': True
            },
            'symbol': {
                'dynamicRegistration': True,
                'symbolKind': {
                    'valueSet': [
                        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                        17, 18, 19, 20, 21, 22, 23, 24, 25, 26
                    ]
                }
            },
            'workspaceEdit': {
                'documentChanges': True
            },
            'workspaceFolders': True
        }
    }
    
    # 指定工作目录
    root_uri = 'file:///C:/Users/DoSun/go/src/github.com/XDfield/go-bilibili-tools'
    workspace_folders = [{'name': 'go-bilibili-tools', 'uri': root_uri}]
    # 指定待检查文件
    file_path = "C:/Users/DoSun/go/src/github.com/XDfield/go-bilibili-tools/bservice/common.go"
    uri = "file:///" + file_path

    lsp_client.initialize(p.pid, None, root_uri, None, capabilities,
                          "messages", workspace_folders)
    lsp_client.initialized()

    text = open(file_path, "r", encoding="utf-8").read()
    languageId = pylspclient.lsp_structs.LANGUAGE_IDENTIFIER.GO
    version = 1

    lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

    print("查找定义:")
    result = lsp_client.definition(pylspclient.lsp_structs.TextDocumentIdentifier(uri), pylspclient.lsp_structs.Position(36, 27))
    for r in result:
        print({
            "uri": r.uri,
            "start": {
                "line": r.range.start.line,
                "char": r.range.start.character
            },
            "end": {
                "line": r.range.end.line,
                "char": r.range.end.character
            }
        })
    print("查找引用:")
    result = lsp_client.references(pylspclient.lsp_structs.TextDocumentIdentifier(uri), pylspclient.lsp_structs.Position(9, 20))
    for r in result:
        print({
            "uri": r.uri,
            "start": {
                "line": r.range.start.line,
                "char": r.range.start.character
            },
            "end": {
                "line": r.range.end.line,
                "char": r.range.end.character
            }
        })

    lsp_client.shutdown()
    lsp_client.exit()

    # p.kill()
