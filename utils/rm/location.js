const dns = require('dns').promises;
const geoip = require('geoip-lite');
const config = require('./config')

Resolver = dns.Resolver;
resolver = new Resolver();
resolver.setServers(config.dnsServers);

function countryOf(ip){
    let geo = geoip.lookup(ip);
    return geo == null ? 'unknown' : geo.country
}

module.exports={
    countryOf,
    async resolve(name){
        const host = String(name || '').replace(/^\[/, '').replace(/\]$/, '')
        const ipv4 = /^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)$/
        const ipv6 = /^[0-9a-fA-F:]+$/
        const domain = /^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/
        if(ipv4.test(host) || (host.includes(':') && ipv6.test(host))){
            return host
        }
        if(!domain.test(host)){
            return null
        }
        try{
            let address = await resolver.resolve4(host);
            if(address && address[0]){
                return address[0]
            }
            return null
        }catch(e){
            return null
        }
    },
    async get(name){
        let ip = await this.resolve(name)
        return ip ? countryOf(ip) : 'unknown'
    }
}
