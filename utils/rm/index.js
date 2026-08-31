const fs = require('fs')
const location = require('./location')
const config = require('./config')

let urls = ''
try {
    urls = fs.readFileSync('./rm2','utf8')
} catch (e) {
    urls = ''
}
let flags = JSON.parse(fs.readFileSync('./flags.json','utf8'))

let urlList = urls.split('\n');
let resList = [];
let stringList = [];
let finalList = [];
let finalURLs = [];
let countryList = ['unknown'];
let emojiList =[''];
let countryCount = {unknown:0};
let urlCountryList = {unknown:[]}

async function run(){
    //处理flags
    for(let i=0;i<flags.length;i++){
        countryList.push(flags[i].code);
        emojiList.push(flags[i].emoji);
        countryCount[flags[i].code] = 0;
        urlCountryList[flags[i].code] = [];
    }

    //解析URL
    for(let i=0;i<urlList.length;i++){
        let url = (urlList[i] || '').trim();
        if(!url || !url.includes('://')){
            continue
        }
        try {
        switch (url.split('://')[0]) {
            case 'vmess':
                let vmessJSON = JSON.parse(Buffer.from(url.split('://')[1], 'base64').toString('utf-8'));
                vmessJSON.ps = null
                resList.push({type: 'vmess', data: vmessJSON, address: vmessJSON.add})
                break
            case 'trojan':
                let trojanData = url.split('://')[1].split('#')[0];
                let trojanAddress = trojanData.split('@')[1].split('?')[0].split(':')[0];
                resList.push({type: 'trojan', data: trojanData, address: trojanAddress})
                break
            case 'ss':
                let ssData = url.split('://')[1].split('#')[0];
                let ssAddress = ssData.split('@')[1].split('#')[0].split(':')[0];
                resList.push({type: 'ss', data: ssData, address: ssAddress})
                break
            case 'ssr':
                let ssrData = Buffer.from(url.split('://')[1], 'base64').toString('utf-8');
                let ssrAddress = ssrData.split(':')[0];
                resList.push({type: 'ssr', data: ssrData.replace(/remarks=.*?(?=&)/, "remarks={name}&"), address: ssrAddress})
                break
            case 'https':
            case 'http':
            case 'socks5':
            case 'socks': {
                let scheme = url.split('://')[0]
                let payload = url.split('://')[1].split('#')[0]
                let hostpart = payload.includes('@') ? payload.split('@')[1] : payload
                hostpart = hostpart.split('?')[0].split('/')[0]
                let address = hostpart.includes(']:') ? hostpart.slice(1, hostpart.indexOf(']:')) : hostpart.split(':')[0]
                resList.push({type: scheme, data: payload, address})
                break
            }
            case 'vless':
            case 'hysteria2':
            case 'hy2':
            case 'anytls':
            case 'tuic':
            case 'hysteria':
            case 'wireguard':
            case 'mieru': {
                let scheme = url.split('://')[0]
                let payload = url.split('://')[1].split('#')[0]
                let hostpart = payload.includes('@') ? payload.split('@')[1] : payload
                hostpart = hostpart.split('?')[0].split('/')[0]
                let address = hostpart.includes(']:') ? hostpart.slice(1, hostpart.indexOf(']:')) : hostpart.split(':')[0]
                resList.push({type: scheme, data: payload, address})
                break
            }
            default:
                break
        }
        } catch (e) {
            continue
        }
    }

    let seenIp = new Set()
    for(let i=0;i<resList.length;i++){
        let ip = await location.resolve(resList[i].address)
        let key = ip || resList[i].address
        if(seenIp.has(key)){
            continue
        }
        seenIp.add(key)
        let country = ip ? location.countryOf(ip) : 'unknown'
        if(!urlCountryList[country]) country = 'unknown'
        resList[i].country = country
        finalList.push(resList[i])
    }

    //变回链接
    for(let i=0;i<finalList.length;i++){
        let item = finalList[i];
        countryCount[finalList[i].country]++
        let name = emojiList[countryList.indexOf(finalList[i].country)]+finalList[i].country+' '+countryCount[finalList[i].country]+config.nodeAddName
        switch (item.type){
            case 'vmess':
                try{
                item.data.ps = (name).toString();
                urlCountryList[finalList[i].country].push('vmess://'+Buffer.from(JSON.stringify(item.data),'utf8').toString('base64'))
                }catch(e){console.log('vmess node err')}
                break
            case 'trojan':
                try{
                urlCountryList[finalList[i].country].push('trojan://'+item.data+'#'+(name).toString())
                }catch(e){console.log('trojan node err')}
                break
            case 'ss':
                try{
                urlCountryList[finalList[i].country].push('ss://'+item.data+'#'+(name).toString())
                }catch(e){console.log('ss node err')}
                break
            case 'ssr':
                try{
                urlCountryList[finalList[i].country].push('ssr://'+Buffer.from(item.data.replace('{name}', Buffer.from((name).toString(),'utf8').toString('base64')),'utf8').toString('base64'))
                }catch(e){console.log('ssr node err')}
                break
            case 'https':
            case 'http':
            case 'socks5':
            case 'socks':
                try{
                urlCountryList[finalList[i].country].push(item.type+'://'+item.data+'#'+encodeURIComponent(name.toString()))
                }catch(e){console.log(item.type+' node err')}
                break
            case 'vless':
            case 'hysteria2':
            case 'hy2':
            case 'anytls':
            case 'tuic':
            case 'hysteria':
            case 'wireguard':
            case 'mieru':
                try{
                urlCountryList[finalList[i].country].push(item.type+'://'+item.data+'#'+encodeURIComponent(name.toString()))
                }catch(e){console.log(item.type+' node err')}
                break
            default:
                break
        }
    }
    for(const i in urlCountryList){
        if(urlCountryList[i].length === 0 ){
        }else{
            for (let a=0;a<urlCountryList[i].length;a++){
                finalURLs.push(urlCountryList[i][a])
            }
        }
    }
    console.log(`去重改名完成\n一共${urlList.length}个节点，去重${urlList.length-finalURLs.length}个节点，剩余${finalURLs.length}个节点`)
    if(finalURLs.length === 0){
        console.log('no URIs after Remove & Remark; not overwriting out')
        return
    }
    fs.writeFileSync('./out',finalURLs.join('\n') + '\n')
}

run()
