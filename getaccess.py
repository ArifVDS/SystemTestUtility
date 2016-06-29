from sherpa import cli_wrapper as cli
accountinfo = cli.clients.scalerim.accountCreate('','user1','user1@test.com')
apikeyinfo = cli.clients.scalerim.apiKeyGenerate('','%s' % accountinfo.canonicalId)
print 'accessKey=%s, secretKey=%s' %(apikeyinfo.accessKey, apikeyinfo.secretKey)
