"""Read public GitHub metadata; no credentials, no tracking pixels or writes."""
import json, os, sys, urllib.error, urllib.request

def get_json(url):
    request=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'qa-fixture-public-interest-check'})
    with urllib.request.urlopen(request,timeout=8) as response:
        return json.load(response)

def main():
    repo=os.getenv('GITHUB_REPOSITORY',sys.argv[1] if len(sys.argv)>1 else '')
    if not repo or repo.count('/')!=1:
        raise SystemExit('Provide public owner/repo as argv[1] or set GITHUB_REPOSITORY')
    base=f'https://api.github.com/repos/{repo}'
    try:
        metadata=get_json(base)
        if metadata.get('private'): raise ValueError('Metrics must be from public repository only')
        result={'repository':repo,'stars':metadata['stargazers_count'],'forks':metadata['forks_count'],'open_issues':metadata['open_issues_count']}
        try:
            release=get_json(base+'/releases/latest')
            result['release_tag']=release.get('tag_name')
            result['release_assets']=[{'name':asset.get('name'),'download_count':asset.get('download_count',0)} for asset in release.get('assets',[])]
        except urllib.error.HTTPError as exc:
            if exc.code!=404: raise
            result['release_assets']=[]
        print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError,ValueError,KeyError) as exc:
        print('metrics_unavailable: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
if __name__=='__main__': main()
