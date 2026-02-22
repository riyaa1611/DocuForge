import React, { useState } from 'react';
import { Copy, Eye, EyeOff, RefreshCw, Trash2, Key, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/services/api';

interface APIKey {
  id: string;
  key: string;
  name: string;
  created_at: string;
  last_used?: string;
}

export const APIKeyManagement = () => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [showNewKey, setShowNewKey] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const loadApiKeys = React.useCallback(async () => {
    try {
      const keys = await api.get<APIKey[]>('/api-keys');
      setApiKeys(keys);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load API keys',
        variant: 'destructive',
      });
    }
  }, [toast]);

  React.useEffect(() => {
    loadApiKeys();
  }, [loadApiKeys]);

  const generateApiKey = async () => {
    setLoading(true);
    try {
      const response = await api.post<{ api_key: string; message: string }>('/api-keys/generate', {
        name: 'Primary API Key',
      });
      setNewApiKey(response.api_key);
      setShowNewKey(true);
      await loadApiKeys();
      toast({
        title: 'Success',
        description: 'API key generated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate API key',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const regenerateApiKey = async () => {
    setLoading(true);
    try {
      const response = await api.post<{ api_key: string; message: string }>('/api-keys/regenerate');
      setNewApiKey(response.api_key);
      setShowNewKey(true);
      await loadApiKeys();
      toast({
        title: 'Success',
        description: 'API key regenerated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to regenerate API key',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const revokeApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await api.delete(`/api-keys/${keyId}`);
      await loadApiKeys();
      toast({
        title: 'Success',
        description: 'API key revoked successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to revoke API key',
        variant: 'destructive',
      });
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied',
      description: 'API key copied to clipboard',
    });
  };

  const toggleKeyVisibility = (keyId: string) => {
    setRevealedKeys((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(keyId)) {
        newSet.delete(keyId);
      } else {
        newSet.add(keyId);
      }
      return newSet;
    });
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>API Key Management</CardTitle>
              <CardDescription>
                Manage API keys for programmatic access to the PDF Generator
              </CardDescription>
            </div>
            <Button onClick={apiKeys.length > 0 ? regenerateApiKey : generateApiKey} disabled={loading}>
              {apiKeys.length > 0 ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Regenerate Key
                </>
              ) : (
                <>
                  <Key className="mr-2 h-4 w-4" />
                  Generate API Key
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {apiKeys.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Key className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>No API keys generated yet</p>
              <p className="text-sm mt-2">Generate an API key to access the API programmatically</p>
            </div>
          ) : (
            <div className="space-y-3">
              {apiKeys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-1 space-y-1">
                    <div className="font-medium">{key.name}</div>
                    <div className="flex items-center gap-2 text-sm font-mono">
                      <code className="bg-muted px-2 py-1 rounded">
                        {revealedKeys.has(key.id) ? key.key : key.key}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleKeyVisibility(key.id)}
                      >
                        {revealedKeys.has(key.id) ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(key.key)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Created: {new Date(key.created_at).toLocaleDateString()}
                      {key.last_used && ` • Last used: ${new Date(key.last_used).toLocaleDateString()}`}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => revokeApiKey(key.id)}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Keep your API keys secure. Do not share them in publicly accessible areas such as GitHub,
              client-side code, etc.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Dialog open={showNewKey} onOpenChange={setShowNewKey}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>API Key Generated</DialogTitle>
            <DialogDescription>
              Make sure to copy your API key now. You won't be able to see it again!
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Your API Key</Label>
              <div className="flex gap-2">
                <Input value={newApiKey} readOnly className="font-mono text-sm" />
                <Button onClick={() => copyToClipboard(newApiKey)}>
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Store this key securely. It will not be displayed again.
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowNewKey(false)}>I've saved my key</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
