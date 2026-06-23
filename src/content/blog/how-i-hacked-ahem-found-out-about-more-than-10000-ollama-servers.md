---
title: How I hacked (ahem) found out about more than 10,000 Ollama servers.
date: 2025-03-04T11:49:00+00:00
slug: how-i-hacked-ahem-found-out-about-more-than-10000-ollama-servers
---

Let's just say that after three shots of espresso in my macchiato, I was feeling productive and decided to set up my own Ollama server on my Oracle instance.

## What is Ollama?

A quick refresher for those unfamiliar:

> _Ollama is an open-source project that serves as a powerful and user-friendly platform for running LLMs on your local machine. It acts as a bridge between the complexities of LLM technology and the desire for an accessible and customizable AI experience._

Yeah, I stole that definition from some random blog, which probably stole it from some AI—it's just incestuous LLM training all the way down. Just to be clear, this blog was **not** written using AI. Not even Grammarly. Yes, my grammar is just that perfect. (Also, that’s why the paragraphs are all over the place.)

But enough about me—let’s get back to the actual content.

## Setting Up the Ollama Server on Oracle VM

As I was configuring the Oracle VM, I had two options:

  * Keep the SSH port (22) open while closing all other ports.
  * Keep all ports open but restrict access to a specific IP address range or an individual IP.



Against my better judgment, I chose the _YOLO_ approach—I opened it to the entire internet and wrote `0.0.0.0/0` in the firewall CIDR notation. My reasoning? "I'm logging in using an SSH key, so it's pretty secure. Plus, I'll be using Tailscale eventually, so I don’t need to worry about other machines or people accessing it."

Eventually, I set up my Ollama server and exposed it on **port 11434**. Then, I discovered that Ollama provides a list of API endpoints to interface with the server. It includes completions and chat endpoints, making it OpenAI-compatible for client interactions.

Then, a wild thought struck me: _What if other people set up an Ollama server just like I did... and left it open to the internet?_

## Finding Open Ollama Servers Online

At this point, I could run an Nmap scan on the entire internet:
[code] 
    nmap -p11434 0.0.0.0/0
    
[/code]

As tempting as that was, it was obviously impractical. Instead, I turned to **Shodan** —a search engine for IoT devices, servers, and even exposed security cameras.

With that knowledge, I searched for:
[code] 
    port:11434 product:"Ollama"
    
[/code]

To my (not really) surprise, I saw **around 10,000 results**. (Hence the blog name. Also, "10,000" just sounds better than "I hacked and controlled 12,343 Ollama servers"—it’s all about the marketing, my friend.) Clicking on these hosts revealed a simple message:

> _Ollama is running._

![Those Magical words](https://i.imgur.com/B22kcab.png)

This demonstrated just how easy it is to find exposed services online if they’re not properly secured.

## Automating the Search with Shodan's API

Since I hold a **lifetime developer subscription** (Black Friday deal, baby!) to Shodan, I had access to its API. And let’s be honest—I wasn’t about to scrape thousands of results manually. So, I asked **GitHub Copilot** to generate a basic Python script (because who remembers `requests` syntax off the top of their head?) to pull a lot of results, IP addresses, and other details.

After scraping about 3,000 hosts, I realized something: my **lifetime developer subscription** lets me click a magical **Download All** button. Each **query credit** gives 100 results, and I get 100 query credits per month—meaning I could download **10,000 results** instantly. Perfect!

![](https://i.imgur.com/ZuG8sOd.png)

Once I had the dataset, I extracted the JSON file and started analyzing it using **Python and Pandas**.

![](https://i.imgur.com/KKFyu5b.png)

Here you can see me absolutely failing at reading the JSON file at first.

## What I Found Might Shock You (But Not Really)

Beyond simply confirming that Ollama was running, the data revealed:

  * **Number of running models** on each server
  * **Specific models installed**
  * **Geographical locations** of each server
  * **Shodan's pre-scanned vulnerability data** for some hosts



To verify whether these servers were still online, I wrote a Python script (exercise left for the reader) that pinged each IP address and checked whether Ollama was active. Since Shodan listings can sometimes be outdated, this was necessary.

![](https://i.imgur.com/QoEeC8g.png)

I found **3,762 active Ollama endpoints**. (Update the blog name accordingly.) ANYWAY!

After compiling this into a **CSV** , I realized something else—I could automate specific **GET requests** to each server, such as:

  * Querying installed models via `/api/tags`
  * **Deleting models** if I really wanted to



![](https://i.imgur.com/NmKUx2c.png)

Almost was tempted into downloading `deepseek-r1:671b`

For more details, check the [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md).

## Could This Be Exploited?

A malicious actor could:

  * Inject **harmful system prompts** into compromised models.
  * **Upload and distribute** malicious models via exposed servers.



However, I didn’t do anything illegal for two reasons:

  1. I want to keep this blog post online.
  2. My primary goal was **exploring Python automation for cybersecurity** , not causing havoc.



That said, combining **automation, AI, and cybersecurity** is an extremely powerful (and potentially dangerous) combination. If you're in **SOC or cybersecurity** , keep this in mind.

## Wrapping Up

If you’re deploying **any** service—**including Ollama** —on a cloud platform, make sure to:

  * **Lock down ports** – Restrict access to trusted IPs or virtual networks.
  * **Use secure credentials** – Self-explanatory.
  * **Enable firewall rules** – Duh.
  * **Monitor logs** – If your bandwidth suddenly spikes, something isn’t right.



## What Did We Learn?

  * **Exposed services = Bad.**
  * **Shodan is powerful** —learn its query documentation.
  * **Always check for a "Download All" button** before scripting a custom scraper.
  * **API endpoints should always be secured** —you never know when a script-kiddie (like me) will start automating things.



## Final Thoughts

If you are running Ollama on a publicly accessible machine—**don't**. But if you absolutely must, then **please** secure it.

Regards,

Your Friendly Neighborhood Python Coder,

Aman Verasia
